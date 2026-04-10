from django.conf import settings
from django.db import models
from django.db.models import F, Q


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        CONFIRMED = "confirmed", "Confirmada"
        PAID = "paid", "Pagada"
        SHIPPED = "shipped", "Enviada"
        DELIVERED = "delivered", "Entregada"
        CANCELED = "canceled", "Cancelada"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    idempotency_key = models.CharField(max_length=64, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, default="")

    shipping_label = models.CharField(max_length=50)
    shipping_address = models.CharField(max_length=255)
    shipping_comuna = models.CharField(max_length=100)
    shipping_region = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "idempotency_key"],
                name="uniq_order_user_idempotency_key",
            ),
            models.CheckConstraint(
                condition=Q(subtotal__gte=0) & Q(shipping_cost__gte=0) & Q(total__gte=0),
                name="order_amounts_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(total=F("subtotal") + F("shipping_cost")),
                name="order_total_matches_subtotal_plus_shipping",
            ),
        ]

    def __str__(self) -> str:
        return f"Orden #{self.pk} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Producto", on_delete=models.PROTECT, related_name="order_items")
    product_name = models.CharField(max_length=100)
    product_slug = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product_name}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(unit_price__gte=0) & Q(line_total__gte=0),
                name="orderitem_amounts_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(line_total=F("unit_price") * F("quantity")),
                name="orderitem_line_total_matches",
            ),
        ]
