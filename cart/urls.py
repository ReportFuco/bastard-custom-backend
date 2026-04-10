from django.urls import path

from .views import CartDetailView, CartHistoryView, AddCartItemView, UpdateCartItemView, ClearCartView

urlpatterns = [
    path("", CartDetailView.as_view(), name="cart-detail"),
    path("history/", CartHistoryView.as_view(), name="cart-history"),
    path("items/", AddCartItemView.as_view(), name="cart-add-item"),
    path("items/<int:item_id>/", UpdateCartItemView.as_view(), name="cart-update-item"),
    path("clear/", ClearCartView.as_view(), name="cart-clear"),
]
