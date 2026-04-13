from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import FranjaPromocional


class PromotionsApiTests(APITestCase):
    def test_bands_endpoint_returns_active_and_in_range(self):
        ahora = timezone.now()
        FranjaPromocional.objects.create(
            titulo="Activa",
            mensaje="Promo vigente",
            etiqueta_cta="Ver",
            url_cta="/productos",
            activa=True,
            fecha_inicio=ahora,
            fecha_fin=ahora + timedelta(days=1),
            prioridad=10,
        )
        FranjaPromocional.objects.create(
            titulo="Inactiva",
            mensaje="No mostrar",
            activa=False,
        )

        response = self.client.get(reverse("promotions-bands"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["titulo"], "Activa")
        self.assertEqual(response.data[0]["message"], "Promo vigente")
