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
    direccion_envio_id = serializers.IntegerField(source="direccion_envio.id", read_only=True, allow_null=True)
    direccion_etiqueta = serializers.CharField(source="direccion_envio.etiqueta", read_only=True, allow_null=True)
    direccion = serializers.CharField(source="direccion_envio.direccion", read_only=True, allow_null=True)
    comuna = serializers.CharField(source="direccion_envio.comuna.nombre", read_only=True, allow_null=True)
    region = serializers.CharField(source="direccion_envio.comuna.region.nombre", read_only=True, allow_null=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "subtotal",
            "shipping_cost",
            "total",
            "notes",
            "direccion_envio_id",
            "direccion_etiqueta",
            "direccion",
            "comuna",
            "region",
            "items",
            "created_at",
            "updated_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    direccion_id = serializers.PrimaryKeyRelatedField(
        queryset=Direccion.objects.all(),
        source="direccion",
        required=False,
        allow_null=True,
    )
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

        self.fields["direccion_id"].queryset = Direccion.objects.filter(usuario=request.user)

    def validate_direccion(self, value):
        request = self.context["request"]
        if not request.user.is_superuser and value.usuario_id != request.user.id:
            raise serializers.ValidationError("La direccion no pertenece al usuario autenticado.")
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        direccion = attrs.get("direccion")
        if direccion is not None:
            return attrs

        request = self.context["request"]
        direccion_por_defecto = (
            Direccion.objects
            .filter(usuario=request.user, es_predeterminada=True)
            .first()
        )
        if direccion_por_defecto is None:
            direccion_por_defecto = (
                Direccion.objects
                .filter(usuario=request.user)
                .order_by("-actualizado_en", "-id")
                .first()
            )

        if direccion_por_defecto is None:
            raise serializers.ValidationError(
                {
                    "direccion_id": (
                        "No tienes direcciones registradas. Crea una en "
                        "/api/users/direcciones/ antes de hacer checkout."
                    )
                }
            )

        attrs["direccion"] = direccion_por_defecto
        return attrs
