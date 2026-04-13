from rest_framework import serializers

from .models import FranjaPromocional


class FranjaPromocionalSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="titulo", read_only=True)
    message = serializers.CharField(source="mensaje", read_only=True)
    ctaLabel = serializers.CharField(source="etiqueta_cta", read_only=True)
    ctaUrl = serializers.CharField(source="url_cta", read_only=True)
    backgroundColor = serializers.CharField(source="color_fondo", read_only=True)
    textColor = serializers.CharField(source="color_texto", read_only=True)

    class Meta:
        model = FranjaPromocional
        fields = [
            "id",
            "titulo",
            "mensaje",
            "etiqueta_cta",
            "url_cta",
            "color_fondo",
            "color_texto",
            "activa",
            "fecha_inicio",
            "fecha_fin",
            "prioridad",
            "creado_en",
            "actualizado_en",
            "title",
            "message",
            "ctaLabel",
            "ctaUrl",
            "backgroundColor",
            "textColor",
        ]
