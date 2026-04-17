from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Categorias, Producto

from .admin import InventoryItemAdmin
from .models import InventoryItem, MovimientoInventario
from .services import InvalidStockAdjustmentError, ajustar_stock

User = get_user_model()


class InventoryPermissionsTests(APITestCase):
    def setUp(self):
        categoria = Categorias.objects.create(nombre="Tecnologia", slug="tecnologia")
        self.producto = Producto.objects.create(
            nombre="Mouse",
            categoria=categoria,
            slug="mouse",
            precio="10000.00",
            activo=True,
        )
        self.inventory_item = self.producto.item_inventario
        self.inventory_item.cantidad_disponible = 5
        self.inventory_item.cantidad_reservada = 2
        self.inventory_item.save(update_fields=["cantidad_disponible", "cantidad_reservada", "actualizado_en"])
        self.url = reverse("inventory-items")
        self.movimientos_url = reverse("inventory-movimientos")
        self.entrada_url = reverse("inventory-item-entrada", kwargs={"pk": self.inventory_item.pk})
        self.ajuste_url = reverse("inventory-item-ajuste", kwargs={"pk": self.inventory_item.pk})
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="12345678",
        )
        self.user = User.objects.create_user(
            username="cliente",
            email="cliente@test.com",
            password="12345678",
        )

    def test_inventory_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inventory_admin_can_see_derived_fields(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["cantidad_total"], 7)
        self.assertTrue(response.data[0]["en_stock"])

    def test_inventory_movimientos_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.movimientos_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inventory_movimientos_admin_can_see_data(self):
        MovimientoInventario.objects.create(
            item_inventario=self.inventory_item,
            tipo=MovimientoInventario.Tipo.AJUSTE,
            cantidad=1,
            cantidad_anterior=5,
            cantidad_posterior=6,
            motivo="Ajuste manual",
            referencia="manual:1",
            creado_por=self.admin,
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.movimientos_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["tipo"], MovimientoInventario.Tipo.AJUSTE)
        self.assertEqual(response.data[0]["producto_nombre"], "Mouse")
        self.assertEqual(response.data[0]["disponible_antes"], 5)
        self.assertEqual(response.data[0]["disponible_despues"], 6)

    def test_inventory_entrada_creates_movement(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            self.entrada_url,
            {"cantidad": 3, "motivo": "Recepcion proveedor", "referencia": "proveedor:1"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.inventory_item.refresh_from_db()
        self.assertEqual(self.inventory_item.cantidad_disponible, 8)
        self.assertEqual(response.data["item"]["cantidad_disponible"], 8)
        self.assertEqual(response.data["movimiento"]["tipo"], MovimientoInventario.Tipo.ENTRADA)

    def test_inventory_ajuste_creates_movement(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            self.ajuste_url,
            {"cantidad_disponible": 9, "motivo": "Conteo", "referencia": "conteo:1"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.inventory_item.refresh_from_db()
        self.assertEqual(self.inventory_item.cantidad_disponible, 9)
        self.assertEqual(response.data["movimiento"]["tipo"], MovimientoInventario.Tipo.AJUSTE)


class InventoryServiceTests(TestCase):
    def setUp(self):
        categoria = Categorias.objects.create(nombre="Food", slug="food")
        producto = Producto.objects.create(
            nombre="Barra",
            categoria=categoria,
            slug="barra",
            precio="1500.00",
            activo=True,
        )
        self.inventory_item = producto.item_inventario
        self.inventory_item.cantidad_disponible = 4
        self.inventory_item.save(update_fields=["cantidad_disponible", "actualizado_en"])

    def test_ajustar_stock_rejects_negative_values(self):
        with self.assertRaises(InvalidStockAdjustmentError):
            ajustar_stock(inventory_item=self.inventory_item, cantidad_disponible=-1)

    def test_ajustar_stock_rejects_noop_adjustment(self):
        with self.assertRaises(InvalidStockAdjustmentError):
            ajustar_stock(inventory_item=self.inventory_item, cantidad_disponible=4)


class InventoryAdminConfigTests(TestCase):
    def test_inventory_item_admin_is_read_only(self):
        site = AdminSite()
        admin_instance = InventoryItemAdmin(InventoryItem, site)
        request = RequestFactory().get("/admin/inventory/inventoryitem/")

        self.assertFalse(admin_instance.has_add_permission(request))
        self.assertFalse(admin_instance.has_delete_permission(request))
        self.assertIn("cantidad_disponible", admin_instance.readonly_fields)
