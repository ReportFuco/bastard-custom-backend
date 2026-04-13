from django.urls import path

from .views import InventoryItemListView, MovimientoInventarioListView

urlpatterns = [
    path("items/", InventoryItemListView.as_view(), name="inventory-items"),
    path("movimientos/", MovimientoInventarioListView.as_view(), name="inventory-movimientos"),
]

