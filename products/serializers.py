from rest_framework import serializers
from .models import (
    Categorias,
    Marca,
    PrecioProducto,
    Producto,
    ProductoColor,
    ProductoImagen,
    Subcategoria,
    TablaNutricional,
)


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias
        fields = ["id", "nombre", "slug"]


class SubcategoriaSerializer(serializers.ModelSerializer):
    categoria_id = serializers.IntegerField(source="categoria.id", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    categoria_slug = serializers.CharField(source="categoria.slug", read_only=True)

    class Meta:
        model = Subcategoria
        fields = [
            "id",
            "nombre",
            "slug",
            "categoria_id",
            "categoria_nombre",
            "categoria_slug",
        ]


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ["id", "nombre", "slug", "pais_origen"]


class PrecioProductoSerializer(serializers.ModelSerializer):
    precio_final = serializers.DecimalField(max_digits=10, decimal_places=2, source="precio_final", read_only=True)

    class Meta:
        model = PrecioProducto
        fields = [
            "precio_lista",
            "precio_oferta",
            "precio_final",
            "moneda",
            "activo",
            "vigencia_desde",
            "vigencia_hasta",
        ]


class ProductoColorSerializer(serializers.ModelSerializer):
    color = serializers.CharField(source="color.hex_code")
    nombre = serializers.CharField(source="color.nombre")

    class Meta:
        model = ProductoColor
        fields = ["color", "nombre"]


class ProductoImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoImagen
        fields = ["imagen", "nombre"]


class TablaNutricionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TablaNutricional
        fields = [
            "porcion",
            "energia_kcal",
            "proteinas_g",
            "grasas_totales_g",
            "grasas_saturadas_g",
            "carbohidratos_g",
            "azucares_g",
            "fibra_g",
            "sodio_mg"
        ]


class ProductoSerializer(serializers.ModelSerializer):
    categoria_id = serializers.IntegerField(source="categoria.id", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    categoria_slug = serializers.CharField(source="categoria.slug", read_only=True)
    marca_id = serializers.IntegerField(source="marca.id", read_only=True)
    marca_nombre = serializers.CharField(source="marca.nombre", read_only=True)
    marca_slug = serializers.CharField(source="marca.slug", read_only=True)
    subcategoria_id = serializers.IntegerField(source="subcategoria.id", read_only=True)
    subcategoria_nombre = serializers.CharField(source="subcategoria.nombre", read_only=True)
    subcategoria_slug = serializers.CharField(source="subcategoria.slug", read_only=True)
    precio_lista = serializers.SerializerMethodField()
    precio_oferta = serializers.SerializerMethodField()
    moneda = serializers.SerializerMethodField()
    imagen_principal = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "slug",
            "categoria_id",
            "categoria_nombre",
            "categoria_slug",
            "marca_id",
            "marca_nombre",
            "marca_slug",
            "subcategoria_id",
            "subcategoria_nombre",
            "subcategoria_slug",
            "precio",
            "precio_lista",
            "precio_oferta",
            "moneda",
            "description",
            "imagen_principal"
        ]

    def get_precio_lista(self, obj: Producto):
        if hasattr(obj, "precio_config"):
            return obj.precio_config.precio_lista
        return obj.precio

    def get_precio_oferta(self, obj: Producto):
        if hasattr(obj, "precio_config"):
            return obj.precio_config.precio_oferta
        return None

    def get_moneda(self, obj: Producto):
        if hasattr(obj, "precio_config"):
            return obj.precio_config.moneda
        return "CLP"

    def get_imagen_principal(self, obj: Producto):
        for imagen in obj.imagenes.all():
            if imagen.principal:
                return ProductoImagenSerializer(imagen).data
        return None


class ProductoDetailSerializer(serializers.ModelSerializer):
    categoria_id = serializers.IntegerField(source="categoria.id", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    categoria_slug = serializers.CharField(source="categoria.slug", read_only=True)
    marca_id = serializers.IntegerField(source="marca.id", read_only=True)
    marca_nombre = serializers.CharField(source="marca.nombre", read_only=True)
    marca_slug = serializers.CharField(source="marca.slug", read_only=True)
    subcategoria_id = serializers.IntegerField(source="subcategoria.id", read_only=True)
    subcategoria_nombre = serializers.CharField(source="subcategoria.nombre", read_only=True)
    subcategoria_slug = serializers.CharField(source="subcategoria.slug", read_only=True)
    precio_info = PrecioProductoSerializer(source="precio_config", read_only=True)
    tabla_nutricional = TablaNutricionalSerializer(read_only=True)
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
            "marca_id",
            "marca_nombre",
            "marca_slug",
            "subcategoria_id",
            "subcategoria_nombre",
            "subcategoria_slug",
            "description",
            "precio_info",
            "tabla_nutricional",
            "variantes_color",
            "imagen_principal",
            "imagenes",
            "created_at",
            "updated_at",
        ]

    def get_imagen_principal(self, obj: Producto):
        for imagen in obj.imagenes.all():
            if imagen.principal:
                return ProductoImagenSerializer(imagen).data
        return None
