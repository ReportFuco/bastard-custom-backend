from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, reverse

from .forms import ProductoAdminForm
from .models import (
    ProductoColor,
    Categorias,
    Marca,
    PrecioProducto,
    Subcategoria,
    TablaNutricional,
    Color,
    Producto,
    ProductoImagen
)


class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1


class PrecioProductoInline(admin.StackedInline):
    model = PrecioProducto
    extra = 0
    max_num = 1


class TablaNutricionalInline(admin.StackedInline):
    model = TablaNutricional
    extra = 0
    max_num = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    form = ProductoAdminForm
    list_display = ("id", "nombre", "marca", "precio", "activo")
    prepopulated_fields = {"slug": ("nombre",)}
    list_filter = ("activo", "categoria", "subcategoria", "marca")
    search_fields = ("nombre", "marca__nombre")
    inlines = [ProductoImagenInline, PrecioProductoInline, TablaNutricionalInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "subcategorias-por-categoria/",
                self.admin_site.admin_view(self.subcategorias_por_categoria_view),
                name="products_producto_subcategorias_por_categoria",
            ),
        ]
        return custom_urls + urls

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        subcategorias_url = reverse("admin:products_producto_subcategorias_por_categoria")
        if "categoria" in form.base_fields:
            form.base_fields["categoria"].widget.attrs["data-subcategorias-url"] = subcategorias_url
        if "categoria" in form.declared_fields:
            form.declared_fields["categoria"].widget.attrs["data-subcategorias-url"] = subcategorias_url
        return form

    def subcategorias_por_categoria_view(self, request):
        categoria_id = request.GET.get("categoria_id")
        subcategoria_qs = Subcategoria.objects.none()
        if categoria_id:
            subcategoria_qs = Subcategoria.objects.filter(
                categoria_id=categoria_id,
            ).order_by("nombre")
        data = {
            "subcategorias": [
                {"id": subcategoria.id, "nombre": subcategoria.nombre}
                for subcategoria in subcategoria_qs
            ]
        }
        return JsonResponse(data)

    class Media:
        js = ("products/js/producto_categoria_subcategoria.js",)


@admin.register(Categorias)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug", "activo")
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "slug", "activo")
    list_filter = ("activo", "categoria")
    search_fields = ("nombre", "categoria__nombre")
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug", "pais_origen", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(PrecioProducto)
class PrecioProductoAdmin(admin.ModelAdmin):
    list_display = ("producto", "precio_lista", "precio_oferta", "moneda", "activo", "updated_at")
    list_filter = ("activo", "moneda")
    search_fields = ("producto__nombre", "producto__slug")


@admin.register(TablaNutricional)
class TablaNutricionalAdmin(admin.ModelAdmin):
    list_display = ("producto", "porcion", "energia_kcal", "proteinas_g", "actualizado_en")
    search_fields = ("producto__nombre", "producto__slug")


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "hex_code", "activo")


@admin.register(ProductoColor)
class ProductoColorAdmin(admin.ModelAdmin):
    list_display = ("producto", "color")


@admin.register(ProductoImagen)
class ProductoImagenAdmin(admin.ModelAdmin):
    list_display = ("producto", "principal")
