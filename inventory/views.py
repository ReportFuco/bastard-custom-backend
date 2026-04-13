from rest_framework import generics, permissions

from .models import InventoryItem, MovimientoInventario
from .serializers import InventoryItemSerializer, MovimientoInventarioSerializer


class InventoryItemListView(generics.ListAPIView):
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return InventoryItem.objects.select_related("producto").order_by("producto__nombre")


class MovimientoInventarioListView(generics.ListAPIView):
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = (
            MovimientoInventario.objects
            .select_related("item_inventario__producto", "creado_por")
            .order_by("-creado_en")
        )

        producto_id = self.request.query_params.get("producto_id")
        if producto_id:
            queryset = queryset.filter(item_inventario__producto_id=producto_id)

        tipo = self.request.query_params.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        return queryset
