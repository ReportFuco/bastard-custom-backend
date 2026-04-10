from django.db import IntegrityError, transaction
from django.db.models import F
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Carrito, ItemCarrito
from .serializers import (
    CarritoSerializer,
    AddItemCarritoSerializer,
    UpdateItemCarritoSerializer,
)


def get_or_create_active_cart(user):
    for attempt in range(2):
        try:
            return Carrito.objects.get_or_create(user=user, status=Carrito.Status.ACTIVE)
        except IntegrityError:
            if attempt == 1:
                raise


class CartDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_cart(self, user):
        carrito, _ = get_or_create_active_cart(user)
        return carrito

    def get(self, request):
        carrito = self.get_cart(request.user)
        carrito = (
            Carrito.objects
            .prefetch_related("items__producto__categoria")
            .get(pk=carrito.pk)
        )
        serializer = CarritoSerializer(carrito)
        return Response(serializer.data)


class CartHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = (
            Carrito.objects
            .filter(user=request.user)
            .prefetch_related("items__producto__categoria")
            .order_by("-created_at")
        )
        return Response(CarritoSerializer(queryset, many=True).data)


class AddCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = AddItemCarritoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        carrito, _ = get_or_create_active_cart(request.user)
        producto = serializer.validated_data["producto"]
        cantidad = serializer.validated_data["cantidad"]

        created = False
        for attempt in range(2):
            try:
                item, created = ItemCarrito.objects.get_or_create(
                    carrito=carrito,
                    producto=producto,
                    defaults={"cantidad": cantidad},
                )
                if not created:
                    ItemCarrito.objects.filter(pk=item.pk).update(cantidad=F("cantidad") + cantidad)
                break
            except IntegrityError:
                if attempt == 1:
                    raise

        carrito.refresh_from_db()
        carrito = Carrito.objects.prefetch_related("items__producto__categoria").get(pk=carrito.pk)
        return Response(CarritoSerializer(carrito).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class UpdateCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def patch(self, request, item_id):
        serializer = UpdateItemCarritoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = ItemCarrito.objects.select_related("carrito", "producto").filter(
            pk=item_id,
            carrito__user=request.user,
            carrito__status=Carrito.Status.ACTIVE,
        ).first()

        if not item:
            return Response({"detail": "Item no encontrado en tu carrito activo."}, status=status.HTTP_404_NOT_FOUND)

        item.cantidad = serializer.validated_data["cantidad"]
        item.save(update_fields=["cantidad"])

        carrito = Carrito.objects.prefetch_related("items__producto__categoria").get(pk=item.carrito_id)
        return Response(CarritoSerializer(carrito).data)

    @transaction.atomic
    def delete(self, request, item_id):
        item = ItemCarrito.objects.select_related("carrito").filter(
            pk=item_id,
            carrito__user=request.user,
            carrito__status=Carrito.Status.ACTIVE,
        ).first()

        if not item:
            return Response({"detail": "Item no encontrado en tu carrito activo."}, status=status.HTTP_404_NOT_FOUND)

        carrito_id = item.carrito_id
        item.delete()

        carrito = Carrito.objects.prefetch_related("items__producto__categoria").get(pk=carrito_id)
        return Response(CarritoSerializer(carrito).data)


class ClearCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def delete(self, request):
        carrito, _ = get_or_create_active_cart(request.user)
        carrito.items.all().delete()
        carrito = Carrito.objects.prefetch_related("items__producto__categoria").get(pk=carrito.pk)
        return Response(CarritoSerializer(carrito).data)
