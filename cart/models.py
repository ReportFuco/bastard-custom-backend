from django.db import models
from django.conf import settings
from django.db.models import Q


class Carrito(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Activo"
        CHECKED_OUT = "checked_out", "Comprado"
        ABANDONED = "abandoned", "Abandonado"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carritos"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    checked_out_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(status="active"),
                name="uniq_active_cart_per_user",
            ),
        ]

    def __str__(self) -> str:
        return f"Carrito {self.get_status_display()} de {self.user}"


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey("products.Producto", on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("carrito", "producto")

    def __str__(self) -> str:
        return f"{self.cantidad} x {self.producto.nombre}"
