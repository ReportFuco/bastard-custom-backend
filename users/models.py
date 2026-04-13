from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q

from .phone import normalize_chile_phone_number


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11, blank=True, default="")
    is_customer = models.BooleanField(default=True)

    REQUIRED_FIELDS = ["email"]

    def save(self, *args, **kwargs):
        self.phone_number = normalize_chile_phone_number(self.phone_number)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username


class Region(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self) -> str:
        return self.nombre
    

class Comuna(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="comunas"
    )

    class Meta:
        unique_together = ("nombre", "region")

    def __str__(self):
        return f"{self.nombre} ({self.region})"


class Direccion(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="direcciones"
    )

    etiqueta = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255)

    comuna = models.ForeignKey(
        Comuna,
        on_delete=models.PROTECT
    )

    es_predeterminada = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario"],
                condition=Q(es_predeterminada=True),
                name="direccion_predeterminada_unica_por_usuario",
            )
        ]
