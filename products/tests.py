from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Categorias, Marca, PrecioProducto, Producto, Subcategoria, TablaNutricional


class ProductsFiltersTests(APITestCase):
    def setUp(self):
        categoria = Categorias.objects.create(nombre="Tecnologia", slug="tecnologia")
        marca = Marca.objects.create(nombre="GenBrand", slug="genbrand")
        subcategoria = Subcategoria.objects.create(
            nombre="Accesorios",
            slug="accesorios",
            categoria=categoria,
        )
        self.producto = Producto.objects.create(
            nombre="Mouse",
            categoria=categoria,
            marca=marca,
            subcategoria=subcategoria,
            slug="mouse",
            precio="10000.00",
            activo=True,
        )

    def test_products_list_is_public(self):
        url = reverse("products-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_categories_list_is_public(self):
        url = reverse("categorias-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_subcategories_list_is_public(self):
        url = reverse("subcategorias-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_brands_list_is_public(self):
        url = reverse("marcas-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_products_post_is_not_allowed(self):
        url = reverse("products-list")
        response = self.client.post(
            url,
            {
                "nombre": "Teclado",
                "slug": "teclado",
                "precio": "15000.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_rejects_invalid_price_filters(self):
        url = reverse("products-list")
        response = self.client.get(url, {"precio_min": "abc"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejects_inverted_price_range(self):
        url = reverse("products-list")
        response = self.client.get(url, {"precio_min": "20000", "precio_max": "10000"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filters_by_subcategory_slug(self):
        url = reverse("products-list")
        response = self.client.get(url, {"subcategoria": "accesorios"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filters_by_brand_slug(self):
        url = reverse("products-list")
        response = self.client.get(url, {"marca": "genbrand"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_price_model_syncs_denormalized_producto_precio(self):
        PrecioProducto.objects.create(
            producto=self.producto,
            precio_lista="24990.00",
            precio_oferta="19990.00",
            moneda="CLP",
            activo=True,
        )
        self.producto.refresh_from_db()
        self.assertEqual(str(self.producto.precio), "19990.00")

    def test_product_detail_includes_tabla_nutricional(self):
        TablaNutricional.objects.create(
            producto=self.producto,
            porcion="100 g",
            energia_kcal="250.00",
            proteinas_g="12.00",
            grasas_totales_g="8.00",
            grasas_saturadas_g="2.50",
            carbohidratos_g="30.00",
            azucares_g="5.00",
            fibra_g="4.00",
            sodio_mg="150.00",
        )

        url = reverse("products-detail", kwargs={"slug": self.producto.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tabla_nutricional", response.data)
        self.assertEqual(response.data["tabla_nutricional"]["porcion"], "100 g")
