from decimal import Decimal

from django.utils import timezone
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Carrito, ItemCarrito
from inventory.models import InventoryItem, MovimientoInventario
from .models import Order, OrderItem
from .serializers import OrderSerializer, CheckoutSerializer


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = (
            Order.objects
            .prefetch_related("items")
        )
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = (
            Order.objects
            .prefetch_related("items")
        )
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(user=self.request.user)


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def calculate_shipping_cost(*, subtotal: Decimal) -> Decimal:
        if subtotal >= Decimal("50000.00"):
            return Decimal("0.00")
        return Decimal("2990.00")

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        idempotency_key = (request.headers.get("Idempotency-Key") or "").strip() or None
        if idempotency_key and len(idempotency_key) > 64:
            return Response(
                {"detail": "Idempotency-Key excede el largo maximo permitido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if idempotency_key:
            existing_order = (
                Order.objects
                .filter(user=request.user, idempotency_key=idempotency_key)
                .prefetch_related("items")
                .first()
            )
            if existing_order:
                return Response(OrderSerializer(existing_order).data, status=status.HTTP_200_OK)

        carrito = (
            Carrito.objects
            .select_for_update()
            .filter(user=request.user, status=Carrito.Status.ACTIVE)
            .first()
        )

        if not carrito:
            return Response({"detail": "El carrito esta vacio."}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = list(
            ItemCarrito.objects
            .select_for_update()
            .select_related("producto", "producto__categoria")
            .filter(carrito=carrito)
        )

        if not cart_items:
            return Response({"detail": "El carrito esta vacio."}, status=status.HTTP_400_BAD_REQUEST)

        invalid_products = []
        for item in cart_items:
            if not item.producto.activo or not item.producto.categoria.activo:
                invalid_products.append(
                    {
                        "product_id": item.producto_id,
                        "nombre": item.producto.nombre,
                        "reason": "inactive_product",
                    }
                )

        if invalid_products:
            return Response(
                {
                    "detail": "Hay productos inactivos en el carrito.",
                    "items": invalid_products,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        direccion = serializer.validated_data["direccion"]
        notes = serializer.validated_data.get("notes", "")

        subtotal = sum(
            (item.producto.precio * item.cantidad for item in cart_items),
            Decimal("0.00"),
        )
        shipping_cost = self.calculate_shipping_cost(subtotal=subtotal)
        total = subtotal + shipping_cost

        product_ids = [item.producto_id for item in cart_items]
        inventory_map = {
            inventory_item.producto_id: inventory_item
            for inventory_item in InventoryItem.objects.select_for_update().filter(producto_id__in=product_ids)
        }

        stock_errors = []
        for item in cart_items:
            inventory_item = inventory_map.get(item.producto_id)
            cantidad_disponible = inventory_item.cantidad_disponible if inventory_item else 0
            if cantidad_disponible < item.cantidad:
                stock_errors.append(
                    {
                        "product_id": item.producto_id,
                        "nombre": item.producto.nombre,
                        "requested": item.cantidad,
                        "available": cantidad_disponible,
                    }
                )

        if stock_errors:
            return Response(
                {
                    "detail": "Stock insuficiente para completar la compra.",
                    "items": stock_errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = Order.objects.create(
            user=request.user,
            idempotency_key=idempotency_key,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total=total,
            notes=notes,
            shipping_label=direccion.etiqueta,
            shipping_address=direccion.direccion,
            shipping_comuna=direccion.comuna.nombre,
            shipping_region=direccion.comuna.region.nombre,
        )

        order_items = []
        for item in cart_items:
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

        movimientos = []
        for item in cart_items:
            inventory_item = inventory_map[item.producto_id]
            cantidad_anterior = inventory_item.cantidad_disponible
            inventory_item.cantidad_disponible -= item.cantidad
            inventory_item.save(update_fields=["cantidad_disponible", "actualizado_en"])
            movimientos.append(
                MovimientoInventario(
                    item_inventario=inventory_item,
                    tipo=MovimientoInventario.Tipo.SALIDA,
                    cantidad=item.cantidad,
                    cantidad_anterior=cantidad_anterior,
                    cantidad_posterior=inventory_item.cantidad_disponible,
                    motivo="Descuento por checkout",
                    referencia=f"order:{order.id}",
                    creado_por=request.user,
                )
            )
        MovimientoInventario.objects.bulk_create(movimientos)

        ItemCarrito.objects.filter(carrito=carrito).delete()
        carrito.status = Carrito.Status.CHECKED_OUT
        carrito.checked_out_at = timezone.now()
        carrito.save(update_fields=["status", "checked_out_at", "updated_at"])
        Carrito.objects.get_or_create(user=request.user, status=Carrito.Status.ACTIVE)

        order = Order.objects.prefetch_related("items").get(pk=order.pk)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
