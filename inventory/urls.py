from django.urls import path

from .views import InventoryItemListView

urlpatterns = [
    path("items/", InventoryItemListView.as_view(), name="inventory-items"),
]

