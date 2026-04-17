from django.db.models.signals import post_save
from django.dispatch import receiver

from products.models import Producto

from .models import InventoryItem


@receiver(post_save, sender=Producto)
def ensure_inventory_item_for_producto(sender, instance, created, **kwargs):
    if not created:
        return
    InventoryItem.objects.get_or_create(producto=instance)
