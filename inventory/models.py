from django.db import models
from django.db.models import Q


class InventoryItem(models.Model):
    producto = models.OneToOneField(
        "products.Producto",
        on_delete=models.CASCADE,
        related_name="item_inventario",
    )
    cantidad_disponible = models.PositiveIntegerField(default=0)
    cantidad_reservada = models.PositiveIntegerField(default=0)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item de inventario"
        verbose_name_plural = "Items de inventario"
        constraints = [
            models.CheckConstraint(
                condition=Q(cantidad_disponible__gte=0) & Q(cantidad_reservada__gte=0),
                name="cantidades_inventario_no_negativas",
            ),
        ]

    @property
    def cantidad_total(self) -> int:
        return self.cantidad_disponible + self.cantidad_reservada

    @property
    def en_stock(self) -> bool:
        return self.cantidad_disponible > 0

    def __str__(self) -> str:
        return f"{self.producto.nombre} - {self.cantidad_disponible} disponibles"


class MovimientoInventario(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = "entrada", "Entrada"
        SALIDA = "salida", "Salida"
        AJUSTE = "ajuste", "Ajuste"
        RESERVA = "reserva", "Reserva"
        LIBERACION = "liberacion", "Liberacion"

    item_inventario = models.ForeignKey(
        "inventory.InventoryItem",
        on_delete=models.CASCADE,
        related_name="movimientos",
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    cantidad = models.PositiveIntegerField()
    cantidad_anterior = models.PositiveIntegerField()
    cantidad_posterior = models.PositiveIntegerField()
    motivo = models.CharField(max_length=255, blank=True)
    referencia = models.CharField(max_length=100, blank=True)
    creado_por = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos_inventario_creados",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Movimientos de inventario"
        ordering = ("-creado_en",)
        constraints = [
            models.CheckConstraint(
                condition=Q(cantidad__gt=0),
                name="movimiento_inventario_cantidad_positiva",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.item_inventario.producto.nombre} | {self.get_tipo_display()} | "
            f"{self.cantidad_anterior}->{self.cantidad_posterior}"
        )
