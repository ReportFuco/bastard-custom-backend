from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ProductoViewSet, CategoriaListView

router = DefaultRouter()
router.register(r"", ProductoViewSet, basename="products")

urlpatterns = [
    path("categorias/", CategoriaListView.as_view(), name="categorias-list"),
] + router.urls
