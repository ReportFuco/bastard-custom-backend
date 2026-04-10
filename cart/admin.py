from django.contrib import admin
from .models import Carrito, ItemCarrito


# Register your models here.
@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "checked_out_at", "created_at", "updated_at")
    search_fields = ("user__username",)
    list_filter = ("status", "created_at", "checked_out_at")

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ("id", "carrito", "producto", "cantidad")
    list_filter = ("producto",)
