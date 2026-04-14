from django.urls import path

from .views import (
    InventoryItemListView,
    MovimientoInventarioListView,
    ProductoProveedorListCreateView,
    ProductoProveedorRetrieveUpdateDestroyView,
    ProveedorListCreateView,
    ProveedorRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("items/", InventoryItemListView.as_view(), name="inventory-items"),
    path("movimientos/", MovimientoInventarioListView.as_view(), name="inventory-movimientos"),
    path("proveedores/", ProveedorListCreateView.as_view(), name="proveedores-list-create"),
    path("proveedores/<int:pk>/", ProveedorRetrieveUpdateDestroyView.as_view(), name="proveedores-detail"),
    path("producto-proveedores/", ProductoProveedorListCreateView.as_view(), name="producto-proveedores-list-create"),
    path(
        "producto-proveedores/<int:pk>/",
        ProductoProveedorRetrieveUpdateDestroyView.as_view(),
        name="producto-proveedores-detail",
    ),
]

