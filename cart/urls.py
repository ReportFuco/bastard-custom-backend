from django.urls import path

from .views import CartDetailView, AddCartItemView, UpdateCartItemView, ClearCartView

urlpatterns = [
    path("", CartDetailView.as_view(), name="cart-detail"),
    path("items/", AddCartItemView.as_view(), name="cart-add-item"),
    path("items/<int:item_id>/", UpdateCartItemView.as_view(), name="cart-update-item"),
    path("clear/", ClearCartView.as_view(), name="cart-clear"),
]
