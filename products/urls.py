from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ProductoViewSet, CategoriaListView, SubcategoriaListView, MarcaListView

router = DefaultRouter()
router.register(r"", ProductoViewSet, basename="products")

urlpatterns = [
    path("categorias/", CategoriaListView.as_view(), name="categorias-list"),
    path("subcategorias/", SubcategoriaListView.as_view(), name="subcategorias-list"),
    path("marcas/", MarcaListView.as_view(), name="marcas-list"),
] + router.urls
