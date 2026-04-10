from decimal import Decimal

from rest_framework import serializers

from users.models import Direccion
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_slug",
            "unit_price",
            "quantity",
            "line_total",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "subtotal",
            "shipping_cost",
            "total",
            "notes",
            "shipping_label",
            "shipping_address",
            "shipping_comuna",
            "shipping_region",
            "items",
            "created_at",
            "updated_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    direccion_id = serializers.PrimaryKeyRelatedField(queryset=Direccion.objects.all(), source="direccion")
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=Decimal("0.00"))
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_direccion(self, value):
        request = self.context["request"]
        if value.user_id != request.user.id:
            raise serializers.ValidationError("La dirección no pertenece al usuario autenticado.")
        return value
