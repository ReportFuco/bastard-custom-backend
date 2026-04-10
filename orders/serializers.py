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
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            self.fields["direccion_id"].queryset = Direccion.objects.none()
            return

        if request.user.is_superuser:
            self.fields["direccion_id"].queryset = Direccion.objects.all()
            return

        self.fields["direccion_id"].queryset = Direccion.objects.filter(user=request.user)

    def validate_direccion(self, value):
        request = self.context["request"]
        if not request.user.is_superuser and value.user_id != request.user.id:
            raise serializers.ValidationError("La direccion no pertenece al usuario autenticado.")
        return value
