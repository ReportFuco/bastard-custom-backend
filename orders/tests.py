from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from cart.models import Carrito, ItemCarrito
from inventory.models import InventoryItem
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
            user=self.user,
            label="Casa",
            direccion="Av Siempre Viva 123",
            comuna=self.comuna,
            is_default=True,
        )

        self.categoria = Categorias.objects.create(nombre="Ropa", slug="ropa")
        self.producto = Producto.objects.create(
            nombre="Polera",
            categoria=self.categoria,
            slug="polera",
            precio="19990.00",
            activo=True,
        )
        InventoryItem.objects.create(product=self.producto, available_quantity=10)

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
        inventory_item = InventoryItem.objects.get(product=self.producto)
        inventory_item.available_quantity = 1
        inventory_item.save(update_fields=["available_quantity"])

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
