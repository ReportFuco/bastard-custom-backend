from decimal import Decimal, InvalidOperation

from django.db.models import F, Q
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Producto, Categorias, Subcategoria, Marca
from .serializers import (
    CategoriaSerializer,
    MarcaSerializer,
    SubcategoriaSerializer,
    ProductoSerializer,
    ProductoDetailSerializer,
)


class CategoriaListView(generics.ListAPIView):
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Categorias.objects.filter(activo=True).order_by("nombre")
        q = self.request.query_params.get("q")
        if q:
            queryset = queryset.filter(nombre__icontains=q)
        return queryset


class SubcategoriaListView(generics.ListAPIView):
    serializer_class = SubcategoriaSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Subcategoria.objects.filter(
            activo=True,
            categoria__activo=True,
        ).select_related("categoria").order_by("nombre")
        q = self.request.query_params.get("q")
        categoria_slug = self.request.query_params.get("categoria")
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) | Q(categoria__nombre__icontains=q)
            )
        if categoria_slug:
            queryset = queryset.filter(categoria__slug=categoria_slug)
        return queryset


class MarcaListView(generics.ListAPIView):
    serializer_class = MarcaSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Marca.objects.filter(activo=True).order_by("nombre")
        q = self.request.query_params.get("q")
        if q:
            queryset = queryset.filter(nombre__icontains=q)
        return queryset


class ProductoViewSet(ReadOnlyModelViewSet):
    lookup_field = "slug"
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Producto.objects.filter(pk=instance.pk).update(vistas=F("vistas") + 1)
        instance.refresh_from_db(fields=["vistas"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = (
            Producto.objects
            .filter(activo=True, categoria__activo=True)
            .select_related("categoria", "subcategoria", "marca", "precio_config", "tabla_nutricional")
            .prefetch_related("imagenes", "variantes_color__color")
            .order_by("-created_at")
        )
        queryset = queryset.filter(Q(marca__activo=True) | Q(marca__isnull=True))

        q = self.request.query_params.get("q")
        categoria_slug = self.request.query_params.get("categoria")
        subcategoria_slug = self.request.query_params.get("subcategoria")
        marca_slug = self.request.query_params.get("marca")
        precio_min = self.request.query_params.get("precio_min")
        precio_max = self.request.query_params.get("precio_max")

        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q)
                | Q(description__icontains=q)
                | Q(categoria__nombre__icontains=q)
                | Q(subcategoria__nombre__icontains=q)
                | Q(marca__nombre__icontains=q)
            )

        if categoria_slug:
            queryset = queryset.filter(categoria__slug=categoria_slug)
        if subcategoria_slug:
            queryset = queryset.filter(subcategoria__slug=subcategoria_slug)
        if marca_slug:
            queryset = queryset.filter(marca__slug=marca_slug)

        if precio_min:
            try:
                precio_min_dec = Decimal(precio_min)
                queryset = queryset.filter(precio__gte=precio_min_dec)
            except (InvalidOperation, ValueError):
                raise ValidationError({"precio_min": "precio_min debe ser numerico."})
        else:
            precio_min_dec = None

        if precio_max:
            try:
                precio_max_dec = Decimal(precio_max)
                queryset = queryset.filter(precio__lte=precio_max_dec)
            except (InvalidOperation, ValueError):
                raise ValidationError({"precio_max": "precio_max debe ser numerico."})
        else:
            precio_max_dec = None

        if precio_min_dec is not None and precio_max_dec is not None and precio_min_dec > precio_max_dec:
            raise ValidationError({"detail": "precio_min no puede ser mayor que precio_max."})

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductoDetailSerializer
        return ProductoSerializer
