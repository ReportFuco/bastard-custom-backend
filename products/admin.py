from django.contrib import admin
from .models import (
    ProductoColor,
    Categorias,
    Color,
    Producto,
    ProductoImagen
)


class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "precio", "activo")
    prepopulated_fields = {"slug": ("nombre",)}
    list_filter = ("activo", "categoria")
    search_fields = ("nombre",)
    inlines = [ProductoImagenInline]


@admin.register(Categorias)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug", "activo")
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "hex_code", "activo")


@admin.register(ProductoColor)
class ProductoColorAdmin(admin.ModelAdmin):
    list_display = ("producto", "color")


@admin.register(ProductoImagen)
class ProductoImagenAdmin(admin.ModelAdmin):
    list_display = ("producto", "principal")
