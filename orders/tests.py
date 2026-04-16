from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from cart.models import Carrito, ItemCarrito
from inventory.models import InventoryItem, MovimientoInventario
from products.models import Categorias, Producto
from users.models import Comuna, Direccion, Region

from .models import Order

User = get_user_model()


class CheckoutFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cliente",
            email="cliente@test.com",
            password="12345678",
        )
        self.client.force_authenticate(user=self.user)

        self.region = Region.objects.create(nombre="Metropolitana")
        self.comuna = Comuna.objects.create(nombre="Santiago", region=self.region)
        self.direccion = Direccion.objects.create(
            usuario=self.user,
            etiqueta="Casa",
            direccion="Av Siempre Viva",
            numero="123",
            comuna=self.comuna,
            es_predeterminada=True,
        )

        self.categoria = Categorias.objects.create(nombre="Ropa", slug="ropa")
        self.producto = Producto.objects.create(
            nombre="Polera",
            categoria=self.categoria,
            slug="polera",
            precio="19990.00",
            activo=True,
        )
        InventoryItem.objects.create(producto=self.producto, cantidad_disponible=10)

        carrito = Carrito.objects.create(user=self.user)
        ItemCarrito.objects.create(carrito=carrito, producto=self.producto, cantidad=2)

    def test_checkout_calculates_shipping_server_side(self):
        url = reverse("orders-checkout")
        response = self.client.post(
            url,
            {"direccion_id": self.direccion.id, "notes": "Entregar rapido"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["subtotal"], "39980.00")
        self.assertEqual(response.data["shipping_cost"], "2990.00")
        self.assertEqual(response.data["total"], "42970.00")

    def test_checkout_is_free_shipping_when_threshold_is_reached(self):
        self.producto.precio = "50000.00"
        self.producto.save(update_fields=["precio"])
        url = reverse("orders-checkout")
        response = self.client.post(url, {"direccion_id": self.direccion.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["shipping_cost"], "0.00")
        self.assertEqual(response.data["total"], response.data["subtotal"])

    def test_checkout_is_idempotent_with_header(self):
        url = reverse("orders-checkout")
        headers = {"HTTP_IDEMPOTENCY_KEY": "idem-123"}

        first = self.client.post(
            url,
            {"direccion_id": self.direccion.id},
            format="json",
            **headers,
        )
        second = self.client.post(
            url,
            {"direccion_id": self.direccion.id},
            format="json",
            **headers,
        )

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data["id"], second.data["id"])
        self.assertEqual(Order.objects.count(), 1)

    def test_checkout_fails_on_insufficient_stock(self):
        inventory_item = InventoryItem.objects.get(producto=self.producto)
        inventory_item.cantidad_disponible = 1
        inventory_item.save(update_fields=["cantidad_disponible"])

        url = reverse("orders-checkout")
        response = self.client.post(url, {"direccion_id": self.direccion.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Stock insuficiente para completar la compra.")

    def test_checkout_fails_if_product_is_inactive(self):
        self.producto.activo = False
        self.producto.save(update_fields=["activo"])
        url = reverse("orders-checkout")
        response = self.client.post(url, {"direccion_id": self.direccion.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Hay productos inactivos en el carrito.")

    def test_checkout_creates_new_active_cart_and_closes_old_one(self):
        previous_cart = Carrito.objects.get(user=self.user, status=Carrito.Status.ACTIVE)
        url = reverse("orders-checkout")
        response = self.client.post(url, {"direccion_id": self.direccion.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        previous_cart.refresh_from_db()
        self.assertEqual(previous_cart.status, Carrito.Status.CHECKED_OUT)
        self.assertIsNotNone(previous_cart.checked_out_at)
        self.assertEqual(Carrito.objects.filter(user=self.user, status=Carrito.Status.ACTIVE).count(), 1)

    def test_checkout_creates_inventory_movement(self):
        url = reverse("orders-checkout")
        response = self.client.post(url, {"direccion_id": self.direccion.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        movimiento = MovimientoInventario.objects.get(
            item_inventario__producto=self.producto,
            tipo=MovimientoInventario.Tipo.SALIDA,
        )
        self.assertEqual(movimiento.cantidad, 2)
        self.assertEqual(movimiento.cantidad_anterior, 10)
        self.assertEqual(movimiento.cantidad_posterior, 8)

    def test_checkout_uses_default_address_if_direccion_id_is_missing(self):
        url = reverse("orders-checkout")
        response = self.client.post(url, {"notes": "sin direccion explicita"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["direccion_etiqueta"], "Casa")
        self.assertEqual(response.data["direccion_envio_id"], self.direccion.id)
        self.assertEqual(response.data["direccion_numero"], "123")

    def test_checkout_fails_if_user_has_no_addresses(self):
        Direccion.objects.filter(usuario=self.user).delete()
        url = reverse("orders-checkout")
        response = self.client.post(url, {"notes": "sin direccion"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("direccion_id", response.data)

    def test_checkout_rejects_address_from_another_user(self):
        otro_usuario = User.objects.create_user(
            username="otro",
            email="otro@test.com",
            password="12345678",
        )
        direccion_ajena = Direccion.objects.create(
            usuario=otro_usuario,
            etiqueta="Ajena",
            direccion="Calle",
            numero="999",
            comuna=self.comuna,
            es_predeterminada=True,
        )
        url = reverse("orders-checkout")
        response = self.client.post(url, {"direccion_id": direccion_ajena.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("direccion_id", response.data)


class OrderAccessIsolationTests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            username="cliente_a",
            email="a@test.com",
            password="12345678",
        )
        self.user_b = User.objects.create_user(
            username="cliente_b",
            email="b@test.com",
            password="12345678",
        )

        region = Region.objects.create(nombre="Metropolitana")
        comuna = Comuna.objects.create(nombre="Santiago", region=region)
        direccion_a = Direccion.objects.create(
            usuario=self.user_a,
            etiqueta="Casa A",
            direccion="Uno",
            numero="1",
            comuna=comuna,
            es_predeterminada=True,
        )
        direccion_b = Direccion.objects.create(
            usuario=self.user_b,
            etiqueta="Casa B",
            direccion="Dos",
            numero="2",
            comuna=comuna,
            es_predeterminada=True,
        )

        self.order_a = Order.objects.create(
            user=self.user_a,
            subtotal="1000.00",
            shipping_cost="0.00",
            total="1000.00",
            direccion_envio=direccion_a,
        )
        self.order_b = Order.objects.create(
            user=self.user_b,
            subtotal="2000.00",
            shipping_cost="0.00",
            total="2000.00",
            direccion_envio=direccion_b,
        )

    def test_orders_list_returns_only_current_user_orders(self):
        self.client.force_authenticate(user=self.user_a)
        url = reverse("orders-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.order_a.id)

    def test_orders_detail_cannot_access_other_user_order(self):
        self.client.force_authenticate(user=self.user_a)
        url = reverse("orders-detail", kwargs={"pk": self.order_b.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderAdminSecurityTests(APITestCase):
    def test_admin_direcciones_por_usuario_endpoint_blocks_other_users_for_staff(self):
        staff = User.objects.create_user(
            username="staff",
            email="staff@test.com",
            password="12345678",
            is_staff=True,
        )
        otro = User.objects.create_user(
            username="otro_admin",
            email="otro_admin@test.com",
            password="12345678",
        )
        region = Region.objects.create(nombre="Metropolitana")
        comuna = Comuna.objects.create(nombre="Santiago", region=region)
        Direccion.objects.create(
            usuario=staff,
            etiqueta="Casa Staff",
            direccion="Uno",
            numero="1",
            comuna=comuna,
            es_predeterminada=True,
        )
        Direccion.objects.create(
            usuario=otro,
            etiqueta="Casa Otro",
            direccion="Dos",
            numero="2",
            comuna=comuna,
            es_predeterminada=True,
        )

        self.client.force_login(staff)
        url = reverse("admin:orders_order_direcciones_por_usuario")
        response_propias = self.client.get(url, {"user_id": staff.id})
        self.assertEqual(response_propias.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_propias.json()["direcciones"]), 1)

        response_ajenas = self.client.get(url, {"user_id": otro.id})
        self.assertEqual(response_ajenas.status_code, status.HTTP_200_OK)
        self.assertEqual(response_ajenas.json()["direcciones"], [])
