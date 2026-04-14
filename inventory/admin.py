from django.contrib import admin

from .models import InventoryItem, MovimientoInventario, ProductoProveedor, Proveedor


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("producto", "cantidad_disponible", "cantidad_reservada", "cantidad_total", "en_stock", "actualizado_en")
    search_fields = ("producto__nombre", "producto__slug")
    list_filter = ("actualizado_en",)
    readonly_fields = ("actualizado_en",)


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = (
        "item_inventario",
        "tipo",
        "cantidad",
        "cantidad_anterior",
        "cantidad_posterior",
        "referencia",
        "creado_por",
        "creado_en",
    )
    search_fields = ("item_inventario__producto__nombre", "item_inventario__producto__slug", "referencia")
    list_filter = ("tipo", "creado_en")
    readonly_fields = ("creado_en",)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = (
        "nombre_proveedor",
        "contacto_proveedor",
        "email_contacto",
        "sitio_web",
        "latitud",
        "longitud",
        "activo",
        "creado_en",
        "actualizado_en",
    )
    search_fields = ("nombre_proveedor", "contacto_proveedor", "email_contacto", "direccion")
    list_filter = ("activo", "creado_en")
    readonly_fields = ("creado_en", "actualizado_en")


@admin.register(ProductoProveedor)
class ProductoProveedorAdmin(admin.ModelAdmin):
    list_display = (
        "producto",
        "proveedor",
        "codigo_proveedor",
        "costo_compra",
        "tiempo_reposicion_dias",
        "activo",
    )
    search_fields = (
        "producto__nombre",
        "producto__slug",
        "proveedor__nombre_proveedor",
        "codigo_proveedor",
    )
    list_filter = ("activo", "proveedor")
    autocomplete_fields = ("producto", "proveedor")
    readonly_fields = ("creado_en", "actualizado_en")
