from rest_framework import generics, permissions

from .models import InventoryItem, MovimientoInventario, ProductoProveedor, Proveedor
from .serializers import (
    InventoryItemSerializer,
    MovimientoInventarioSerializer,
    ProductoProveedorSerializer,
    ProveedorSerializer,
)


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
