from django.contrib import admin

from .models import InventoryItem


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("product", "available_quantity", "reserved_quantity", "updated_at")
    search_fields = ("product__nombre", "product__slug")
