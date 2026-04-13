from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from .models import Comuna, Direccion, Region

User = get_user_model()


class DireccionConstraintsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cliente",
            email="cliente2@test.com",
            password="12345678",
        )
        region = Region.objects.create(nombre="Valparaiso")
        self.comuna = Comuna.objects.create(nombre="Vina del Mar", region=region)

    def test_only_one_default_address_per_user(self):
        Direccion.objects.create(
            usuario=self.user,
            etiqueta="Casa",
            direccion="Uno",
            comuna=self.comuna,
            es_predeterminada=True,
        )

        with self.assertRaises(IntegrityError):
            Direccion.objects.create(
                usuario=self.user,
                etiqueta="Oficina",
                direccion="Dos",
                comuna=self.comuna,
                es_predeterminada=True,
            )
