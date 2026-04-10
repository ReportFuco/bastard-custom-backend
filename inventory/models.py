from django.db import models
from django.db.models import F, Q


class InventoryItem(models.Model):
    product = models.OneToOneField(
        "products.Producto",
        on_delete=models.CASCADE,
        related_name="inventory_item",
    )
    available_quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inventory item"
        verbose_name_plural = "Inventory items"
        constraints = [
            models.CheckConstraint(
                condition=Q(available_quantity__gte=0) & Q(reserved_quantity__gte=0),
                name="inventory_quantities_non_negative",
            ),
        ]

    @property
    def total_quantity(self) -> int:
        return self.available_quantity + self.reserved_quantity

    @property
    def in_stock(self) -> bool:
        return self.available_quantity > 0

    def __str__(self) -> str:
        return f"{self.product.nombre} - {self.available_quantity} disponibles"
