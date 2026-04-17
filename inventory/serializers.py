from rest_framework import serializers

from .models import InventoryItem, MovimientoInventario, ProductoProveedor, Proveedor


class InventoryItemSerializer(serializers.ModelSerializer):
    producto_id = serializers.IntegerField(source="producto.id", read_only=True)
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    producto_slug = serializers.CharField(source="producto.slug", read_only=True)
    cantidad_total = serializers.IntegerField(read_only=True)
    en_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "producto_id",
            "producto_nombre",
            "producto_slug",
            "cantidad_disponible",
            "cantidad_reservada",
            "cantidad_total",
            "en_stock",
            "actualizado_en",
        ]


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    producto_id = serializers.IntegerField(source="item_inventario.producto.id", read_only=True)
    producto_nombre = serializers.CharField(source="item_inventario.producto.nombre", read_only=True)
    item_inventario_id = serializers.IntegerField(source="item_inventario.id", read_only=True)
    creado_por_id = serializers.IntegerField(source="creado_por.id", read_only=True)
    creado_por_username = serializers.CharField(source="creado_por.username", read_only=True)
    disponible_antes = serializers.IntegerField(source="cantidad_anterior", read_only=True)
    disponible_despues = serializers.IntegerField(source="cantidad_posterior", read_only=True)

    class Meta:
        model = MovimientoInventario
        fields = [
            "id",
            "item_inventario_id",
            "producto_id",
            "producto_nombre",
            "tipo",
            "cantidad",
            "cantidad_anterior",
            "cantidad_posterior",
            "disponible_antes",
            "disponible_despues",
            "motivo",
            "referencia",
            "creado_por_id",
            "creado_por_username",
            "creado_en",
        ]


class InventoryEntradaSerializer(serializers.Serializer):
    cantidad = serializers.IntegerField(min_value=1)
    motivo = serializers.CharField(required=False, allow_blank=True, default="")
    referencia = serializers.CharField(required=False, allow_blank=True, default="")


class InventoryAjusteSerializer(serializers.Serializer):
    cantidad_disponible = serializers.IntegerField(min_value=0)
    motivo = serializers.CharField(required=False, allow_blank=True, default="")
    referencia = serializers.CharField(required=False, allow_blank=True, default="")


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = [
            "id",
            "nombre_proveedor",
            "contacto_proveedor",
            "email_contacto",
            "sitio_web",
            "direccion",
            "latitud",
            "longitud",
            "activo",
            "creado_en",
            "actualizado_en",
        ]


class ProductoProveedorSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    proveedor_nombre = serializers.CharField(source="proveedor.nombre_proveedor", read_only=True)

    class Meta:
        model = ProductoProveedor
        fields = [
            "id",
            "producto",
            "producto_nombre",
            "proveedor",
            "proveedor_nombre",
            "codigo_proveedor",
            "costo_compra",
            "tiempo_reposicion_dias",
            "activo",
            "creado_en",
            "actualizado_en",
        ]
