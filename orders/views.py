from decimal import Decimal

from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Carrito
from .models import Order, OrderItem
from .serializers import OrderSerializer, CheckoutSerializer


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related("items")
        )


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related("items")
        )


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        carrito = (
            Carrito.objects
            .prefetch_related("items__producto", "user")
            .filter(user=request.user)
            .first()
        )

        if not carrito or not carrito.items.exists():
            return Response({"detail": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        direccion = serializer.validated_data["direccion"]
        shipping_cost = serializer.validated_data.get("shipping_cost", Decimal("0.00"))
        notes = serializer.validated_data.get("notes", "")

        subtotal = sum(
            (item.producto.precio * item.cantidad for item in carrito.items.all()),
            Decimal("0.00"),
        )
        total = subtotal + shipping_cost

        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total=total,
            notes=notes,
            shipping_label=direccion.label,
            shipping_address=direccion.direccion,
            shipping_comuna=direccion.comuna.nombre,
            shipping_region=direccion.comuna.region.nombre,
        )

        order_items = []
        for item in carrito.items.all():
            order_items.append(
                OrderItem(
                    order=order,
                    product=item.producto,
                    product_name=item.producto.nombre,
                    product_slug=item.producto.slug,
                    unit_price=item.producto.precio,
                    quantity=item.cantidad,
                    line_total=item.producto.precio * item.cantidad,
                )
            )

        OrderItem.objects.bulk_create(order_items)
        carrito.items.all().delete()

        order = Order.objects.prefetch_related("items").get(pk=order.pk)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
