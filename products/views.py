from django.db.models import Q
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Producto
from .serializers import (
    ProductoSerializer,
    ProductoDetailSerializer
)


class ProductoViewSet(ReadOnlyModelViewSet):
    serializer_class = ProductoSerializer

    def get_queryset(self):
        queryset = (
            Producto.objects
            .filter(activo=True)
            .select_related("categoria")
            .prefetch_related(
                "imagenes",
                "variantes_color__color"
            )
        )

        q = self.request.query_params.get("q")

        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) |
                Q(description__icontains=q) |
                Q(categoria__nombre__icontains=q)
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductoDetailSerializer
        return ProductoSerializer
