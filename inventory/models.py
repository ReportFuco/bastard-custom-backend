from django.db import models


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

    def __str__(self) -> str:
        return f"{self.product.nombre} - {self.available_quantity} disponibles"
