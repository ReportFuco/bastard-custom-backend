from rest_framework import generics, permissions

from .models import InventoryItem
from .serializers import InventoryItemSerializer


class InventoryItemListView(generics.ListAPIView):
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return InventoryItem.objects.select_related("product").order_by("product__nombre")
