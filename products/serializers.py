from rest_framework import serializers
from .models import (
    Categorias,
    Producto,
    ProductoColor,
    ProductoImagen,
)


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias
        fields = ["id", "nombre", "slug"]


class ProductoColorSerializer(serializers.ModelSerializer):
    color = serializers.CharField(source="color.hex_code")
    nombre = serializers.CharField(source="color.nombre")

    class Meta:
        model = ProductoColor
        fields = ["color", "nombre"]


class ProductoImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoImagen
        fields = ["imagen", "nombre", "principal"]


class ProductoSerializer(serializers.ModelSerializer):
    categoria_id = serializers.IntegerField(source="categoria.id", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre")
    categoria_slug = serializers.CharField(source="categoria.slug", read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "slug",
            "categoria_id",
            "categoria_nombre",
            "categoria_slug",
            "precio",
            "description",
            "created_at",
            "updated_at",
        ]


class ProductoDetailSerializer(serializers.ModelSerializer):
    categoria_id = serializers.IntegerField(source="categoria.id", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre")
    categoria_slug = serializers.CharField(source="categoria.slug", read_only=True)
    imagen_principal = serializers.SerializerMethodField()
    imagenes = ProductoImagenSerializer(many=True)
    variantes_color = ProductoColorSerializer(many=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "slug",
            "precio",
            "categoria_id",
            "categoria_nombre",
            "categoria_slug",
            "description",
            "variantes_color",
            "imagen_principal",
            "imagenes",
            "created_at",
            "updated_at",
        ]

    def get_imagen_principal(self, obj: Producto):
        imagen = obj.imagenes.filter(principal=True).first()
        return ProductoImagenSerializer(imagen).data if imagen else None
