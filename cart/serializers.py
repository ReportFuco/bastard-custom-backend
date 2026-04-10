from decimal import Decimal

from rest_framework import serializers

from .models import Carrito, ItemCarrito
from products.models import Producto


class CartItemProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)

    class Meta:
        model = Producto
        fields = ["id", "nombre", "slug", "precio", "categoria_nombre"]


class ItemCarritoSerializer(serializers.ModelSerializer):
    producto = CartItemProductoSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemCarrito
        fields = ["id", "producto", "cantidad", "subtotal"]

    def get_subtotal(self, obj):
        return obj.producto.precio * obj.cantidad


class CarritoSerializer(serializers.ModelSerializer):
    items = ItemCarritoSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Carrito
        fields = ["id", "created_at", "updated_at", "total_items", "total", "items"]

    def get_total_items(self, obj):
        return sum(item.cantidad for item in obj.items.all())

    def get_total(self, obj):
        total = sum((item.producto.precio * item.cantidad for item in obj.items.all()), Decimal("0"))
        return total


class AddItemCarritoSerializer(serializers.Serializer):
    producto_id = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.filter(activo=True), source="producto")
    cantidad = serializers.IntegerField(min_value=1, default=1)


class UpdateItemCarritoSerializer(serializers.Serializer):
    cantidad = serializers.IntegerField(min_value=1)
