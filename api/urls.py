from django.urls import path, include

urlpatterns = [
    path("users/", include("users.urls")),
    path("products/", include("products.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("inventory/", include("inventory.urls")),
    path("promotions/", include("promotions.urls")),
]
