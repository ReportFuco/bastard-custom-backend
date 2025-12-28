from rest_framework import serializers
from .models import (
    Producto,
    ProductoColor,
    ProductoImagen,
)

class ProductoColorSerializer(serializers.ModelSerializer):
    color = serializers.CharField(source="color.hex_code")
    nombre = serializers.CharField(source="color.nombre")
    class Meta:
        model = ProductoColor
        fields = ["color", "nombre"]

class ProductoImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoImagen
        fields = ["imagen"]



class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre")
    class Meta:
        model = Producto
        fields = [
            "id", "nombre", "categoria_nombre", "precio", "description", "created_at"
        ]

class ProductoDetailSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre")
    imagen_principal = serializers.SerializerMethodField()
    imagenes = ProductoImagenSerializer(many=True)
    variantes_color = ProductoColorSerializer(many=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "precio",
            "categoria_nombre",
            "description",
            "variantes_color",
            "imagen_principal",
            "imagenes",
        ]

    def get_imagen_principal(self, obj:Producto):
        imagen = obj.imagenes.filter(principal=True).first()
        return (
            ProductoImagenSerializer(imagen).data
            if imagen else None
        )
