from django.urls import path

from .views import OrderListView, OrderDetailView, CheckoutView

urlpatterns = [
    path("", OrderListView.as_view(), name="orders-list"),
    path("checkout/", CheckoutView.as_view(), name="orders-checkout"),
    path("<int:pk>/", OrderDetailView.as_view(), name="orders-detail"),
]
