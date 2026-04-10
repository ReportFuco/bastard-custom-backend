from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import JsonResponse
from django.urls import path, reverse

from .forms import DireccionAdminForm, UserAdminCreationForm, UserAdminChangeForm
from .models import (
    Comuna, User, Direccion, Region
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    list_display = ("username", "email", "phone_number", "is_customer", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("Extra info", {"fields": ("phone_number", "is_customer")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra info", {"fields": ("email", "phone_number", "is_customer")}),
    )


@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    form = DireccionAdminForm
    list_display = ("user", "label", "direccion", "comuna", "is_default", "created_at")
    list_filter = ("is_default", "comuna__region")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "comunas-por-region/",
                self.admin_site.admin_view(self.comunas_por_region_view),
                name="users_direccion_comunas_por_region",
            ),
        ]
        return custom_urls + urls

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        comunas_url = reverse("admin:users_direccion_comunas_por_region")
        if "region" in form.base_fields:
            form.base_fields["region"].widget.attrs["data-comunas-url"] = comunas_url
        if "region" in form.declared_fields:
            form.declared_fields["region"].widget.attrs["data-comunas-url"] = comunas_url
        return form

    def comunas_por_region_view(self, request):
        region_id = request.GET.get("region_id")
        comuna_qs = Comuna.objects.none()

        if region_id:
            comuna_qs = Comuna.objects.filter(region_id=region_id).order_by("nombre")

        data = {
            "comunas": [{"id": comuna.id, "nombre": comuna.nombre} for comuna in comuna_qs]
        }
        return JsonResponse(data)

    class Media:
        js = ("users/js/direccion_region_comuna.js",)


@admin.register(Comuna)
class ComunaAdmin(admin.ModelAdmin):
    model = Comuna
    list_display = ("nombre", "region")


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ["nombre"]
