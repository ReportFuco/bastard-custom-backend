from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Categorias, Producto


class ProductsFiltersTests(APITestCase):
    def setUp(self):
        categoria = Categorias.objects.create(nombre="Tecnologia", slug="tecnologia")
        Producto.objects.create(
            nombre="Mouse",
            categoria=categoria,
            slug="mouse",
            precio="10000.00",
            activo=True,
        )

    def test_rejects_invalid_price_filters(self):
        url = reverse("products-list")
        response = self.client.get(url, {"precio_min": "abc"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejects_inverted_price_range(self):
        url = reverse("products-list")
        response = self.client.get(url, {"precio_min": "20000", "precio_max": "10000"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
