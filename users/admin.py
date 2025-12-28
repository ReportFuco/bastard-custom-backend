from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Comuna, User, Direccion, Region
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("username", "email", "is_customer", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("Extra info", {"fields": ("is_customer",)}),
    )


@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ("user", "label", "direccion", "comuna", "created_at")


@admin.register(Comuna)
class ComunaAdmin(admin.ModelAdmin):
    model = Comuna
    list_display = ("nombre", "region")


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ["nombre"]