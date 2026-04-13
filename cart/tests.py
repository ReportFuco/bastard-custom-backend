from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from inventory.models import InventoryItem
from products.models import Categorias, Producto
from users.models import Comuna, Direccion, Region

from .models import Carrito, ItemCarrito

User = get_user_model()


class CartHistoryTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="historyuser",
            email="history@test.com",
            password="12345678",
        )
        self.client.force_authenticate(user=self.user)

        region = Region.objects.create(nombre="Metropolitana")
        comuna = Comuna.objects.create(nombre="Santiago", region=region)
        self.direccion = Direccion.objects.create(
            user=self.user,
            label="Casa",
            direccion="Uno",
            comuna=comuna,
            is_default=True,
        )

        categoria = Categorias.objects.create(nombre="Accesorios", slug="accesorios")
        self.producto = Producto.objects.create(
            nombre="Cable",
            categoria=categoria,
            slug="cable",
            precio="10000.00",
            activo=True,
        )
        InventoryItem.objects.create(producto=self.producto, cantidad_disponible=10)

    def test_checkout_closes_active_cart_and_creates_new_one(self):
        carrito = Carrito.objects.create(user=self.user, status=Carrito.Status.ACTIVE)
        ItemCarrito.objects.create(carrito=carrito, producto=self.producto, cantidad=1)

        checkout_url = reverse("orders-checkout")
        response = self.client.post(checkout_url, {"direccion_id": self.direccion.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        old_cart = Carrito.objects.get(pk=carrito.pk)
        self.assertEqual(old_cart.status, Carrito.Status.CHECKED_OUT)
        self.assertIsNotNone(old_cart.checked_out_at)

        active_count = Carrito.objects.filter(user=self.user, status=Carrito.Status.ACTIVE).count()
        self.assertEqual(active_count, 1)

    def test_cart_history_lists_multiple_carts(self):
        active_cart = Carrito.objects.create(user=self.user, status=Carrito.Status.ACTIVE)
        old_cart = Carrito.objects.create(user=self.user, status=Carrito.Status.CHECKED_OUT)
        ItemCarrito.objects.create(carrito=active_cart, producto=self.producto, cantidad=1)
        ItemCarrito.objects.create(carrito=old_cart, producto=self.producto, cantidad=2)

        history_url = reverse("cart-history")
        response = self.client.get(history_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
