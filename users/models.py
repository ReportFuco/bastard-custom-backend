from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_customer = models.BooleanField(default=True)

    REQUIRED_FIELDS = ["email"]

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
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="direcciones"
    )

    label = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255)

    comuna = models.ForeignKey(
        Comuna,
        on_delete=models.PROTECT
    )

    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)