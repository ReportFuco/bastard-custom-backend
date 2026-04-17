from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import InventoryItem, MovimientoInventario, ProductoProveedor, Proveedor
from .serializers import (
    InventoryAjusteSerializer,
    InventoryEntradaSerializer,
    InventoryItemSerializer,
    MovimientoInventarioSerializer,
    ProductoProveedorSerializer,
    ProveedorSerializer,
)
from .services import InvalidStockAdjustmentError, ajustar_stock, registrar_entrada_stock


class InventoryItemListView(generics.ListAPIView):
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return InventoryItem.objects.select_related("producto").order_by("producto__nombre")


class InventoryEntradaView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @transaction.atomic
    def post(self, request, pk):
        inventory_item = InventoryItem.objects.select_related("producto").filter(pk=pk).first()
        if not inventory_item:
            return Response({"detail": "Item de inventario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = InventoryEntradaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            movimiento = registrar_entrada_stock(
                inventory_item=inventory_item,
                cantidad=serializer.validated_data["cantidad"],
                actor=request.user,
                motivo=serializer.validated_data.get("motivo") or "Entrada manual de stock",
                referencia=serializer.validated_data.get("referencia", ""),
            )
        except InvalidStockAdjustmentError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        inventory_item.refresh_from_db()
        return Response(
            {
                "item": InventoryItemSerializer(inventory_item).data,
                "movimiento": MovimientoInventarioSerializer(movimiento).data,
            }
        )


class InventoryAjusteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @transaction.atomic
    def post(self, request, pk):
        inventory_item = InventoryItem.objects.select_related("producto").filter(pk=pk).first()
        if not inventory_item:
            return Response({"detail": "Item de inventario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = InventoryAjusteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            movimiento = ajustar_stock(
                inventory_item=inventory_item,
                cantidad_disponible=serializer.validated_data["cantidad_disponible"],
                actor=request.user,
                motivo=serializer.validated_data.get("motivo") or "Ajuste manual de stock",
                referencia=serializer.validated_data.get("referencia", ""),
            )
        except InvalidStockAdjustmentError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        inventory_item.refresh_from_db()
        return Response(
            {
                "item": InventoryItemSerializer(inventory_item).data,
                "movimiento": MovimientoInventarioSerializer(movimiento).data,
            }
        )


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


class ProveedorListCreateView(generics.ListCreateAPIView):
    serializer_class = ProveedorSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = Proveedor.objects.order_by("nombre_proveedor")
        q = self.request.query_params.get("q")
        if q:
            queryset = queryset.filter(nombre_proveedor__icontains=q)
        return queryset


class ProveedorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProveedorSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Proveedor.objects.all()


class ProductoProveedorListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductoProveedorSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = (
            ProductoProveedor.objects
            .select_related("producto", "proveedor")
            .order_by("producto__nombre", "proveedor__nombre_proveedor")
        )
        producto_id = self.request.query_params.get("producto_id")
        if producto_id:
            queryset = queryset.filter(producto_id=producto_id)

        proveedor_id = self.request.query_params.get("proveedor_id")
        if proveedor_id:
            queryset = queryset.filter(proveedor_id=proveedor_id)

        return queryset


class ProductoProveedorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductoProveedorSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ProductoProveedor.objects.select_related("producto", "proveedor")
