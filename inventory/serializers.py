from rest_framework import serializers

from .models import InventoryItem


class InventoryItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.nombre", read_only=True)
    product_slug = serializers.CharField(source="product.slug", read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "product_id",
            "product_name",
            "product_slug",
            "available_quantity",
            "reserved_quantity",
            "updated_at",
        ]
