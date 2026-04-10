from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Categorias, Producto
from .models import InventoryItem

User = get_user_model()


class InventoryPermissionsTests(APITestCase):
    def setUp(self):
        categoria = Categorias.objects.create(nombre="Tecnologia", slug="tecnologia")
        producto = Producto.objects.create(
            nombre="Mouse",
            categoria=categoria,
            slug="mouse",
            precio="10000.00",
            activo=True,
        )
        InventoryItem.objects.create(product=producto, available_quantity=5, reserved_quantity=2)
        self.url = reverse("inventory-items")
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
        self.assertEqual(response.data[0]["total_quantity"], 7)
        self.assertTrue(response.data[0]["in_stock"])
