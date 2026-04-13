from django.contrib import admin

from .forms import FranjaPromocionalAdminForm
from .models import FranjaPromocional


@admin.register(FranjaPromocional)
class FranjaPromocionalAdmin(admin.ModelAdmin):
    form = FranjaPromocionalAdminForm
    list_display = ("titulo", "activa", "prioridad", "fecha_inicio", "fecha_fin", "actualizado_en")
    list_filter = ("activa", "fecha_inicio", "fecha_fin")
    search_fields = ("titulo", "mensaje")
