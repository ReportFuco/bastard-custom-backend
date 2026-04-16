from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, reverse

from .forms import OrderAdminForm, OrderItemAdminForm
from .models import Order, OrderItem
from users.models import Direccion


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    form = OrderItemAdminForm
    extra = 0
    fields = ("product_slug", "producto_mostrado", "nombre_producto", "precio_unitario", "cantidad_item", "total_linea")
    readonly_fields = ("producto_mostrado", "nombre_producto", "precio_unitario", "cantidad_item", "total_linea")

    @admin.display(description="Producto")
    def producto_mostrado(self, obj):
        if obj is None:
            return "-"
        return obj.product

    @admin.display(description="Nombre de producto")
    def nombre_producto(self, obj):
        if obj is None:
            return "-"
        return obj.product_name

    @admin.display(description="Precio unitario")
    def precio_unitario(self, obj):
        if obj is None:
            return "-"
        return obj.unit_price

    @admin.display(description="Cantidad")
    def cantidad_item(self, obj):
        if obj is None:
            return "-"
        return obj.quantity

    @admin.display(description="Total línea")
    def total_linea(self, obj):
        if obj is None:
            return "-"
        return obj.line_total


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ("id", "user", "status", "total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "direccion_envio__direccion")
    fieldsets = (
        ("Cliente", {"fields": ("user", "status", "idempotency_key")}),
        ("Montos", {"fields": ("subtotal", "shipping_cost", "total")}),
        ("Dirección de envío", {"fields": ("direccion_envio",)}),
        ("Notas", {"fields": ("notes",)}),
        ("Trazabilidad", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user=request.user)

    def has_view_permission(self, request, obj=None):
        permiso_base = super().has_view_permission(request, obj)
        if not permiso_base:
            return False
        if obj is None or request.user.is_superuser:
            return True
        return obj.user_id == request.user.id

    def has_change_permission(self, request, obj=None):
        permiso_base = super().has_change_permission(request, obj)
        if not permiso_base:
            return False
        if obj is None or request.user.is_superuser:
            return True
        return obj.user_id == request.user.id

    def has_delete_permission(self, request, obj=None):
        permiso_base = super().has_delete_permission(request, obj)
        if not permiso_base:
            return False
        if obj is None or request.user.is_superuser:
            return True
        return obj.user_id == request.user.id

    def has_add_permission(self, request):
        # Las ordenes deben generarse desde checkout; alta manual solo superusuario.
        return request.user.is_superuser and super().has_add_permission(request)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser and "user" not in readonly_fields:
            readonly_fields.append("user")
        return tuple(readonly_fields)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "direcciones-por-usuario/",
                self.admin_site.admin_view(self.direcciones_por_usuario_view),
                name="orders_order_direcciones_por_usuario",
            ),
        ]
        return custom_urls + urls

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        direcciones_url = reverse("admin:orders_order_direcciones_por_usuario")
        if "user" in form.base_fields:
            form.base_fields["user"].widget.attrs["data-direcciones-url"] = direcciones_url
        if "user" in form.declared_fields:
            form.declared_fields["user"].widget.attrs["data-direcciones-url"] = direcciones_url
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user" and not request.user.is_superuser:
            kwargs["queryset"] = type(request.user).objects.filter(pk=request.user.pk)
        if db_field.name == "direccion_envio":
            user_id = request.POST.get("user")
            if not user_id:
                object_id = request.resolver_match.kwargs.get("object_id") if request.resolver_match else None
                if object_id:
                    order = Order.objects.filter(pk=object_id).only("user_id").first()
                    if order:
                        user_id = str(order.user_id)
            if user_id and user_id.isdigit():
                kwargs["queryset"] = Direccion.objects.filter(usuario_id=user_id).select_related("comuna__region")
            else:
                kwargs["queryset"] = Direccion.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def direcciones_por_usuario_view(self, request):
        user_id = request.GET.get("user_id")
        direcciones = Direccion.objects.none()
        if user_id and user_id.isdigit():
            if not request.user.is_superuser and int(user_id) != request.user.id:
                return JsonResponse({"direcciones": []})
            direcciones = (
                Direccion.objects
                .filter(usuario_id=user_id)
                .select_related("comuna__region")
                .order_by("-es_predeterminada", "etiqueta", "id")
            )

        data = {
            "direcciones": [
                {
                    "id": direccion.id,
                    "texto": (
                        f"{direccion.etiqueta} - {direccion.direccion} {direccion.numero}".strip()
                        + " "
                        f"({direccion.comuna.nombre}, {direccion.comuna.region.nombre})"
                    ),
                }
                for direccion in direcciones
            ]
        }
        return JsonResponse(data)

    class Media:
        js = ("orders/js/order_usuario_direccion.js",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    form = OrderItemAdminForm
    list_display = ("id", "order", "product_name", "quantity", "line_total")
    search_fields = ("product_name", "product_slug")

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related("order")
        if request.user.is_superuser:
            return queryset
        return queryset.filter(order__user=request.user)
