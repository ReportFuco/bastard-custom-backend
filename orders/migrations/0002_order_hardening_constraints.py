# Generated manually

from django.db import migrations, models
from django.db.models import F, Q


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="idempotency_key",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddConstraint(
            model_name="order",
            constraint=models.UniqueConstraint(
                fields=("user", "idempotency_key"),
                name="uniq_order_user_idempotency_key",
            ),
        ),
        migrations.AddConstraint(
            model_name="order",
            constraint=models.CheckConstraint(
                condition=Q(subtotal__gte=0) & Q(shipping_cost__gte=0) & Q(total__gte=0),
                name="order_amounts_non_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="order",
            constraint=models.CheckConstraint(
                condition=Q(total=F("subtotal") + F("shipping_cost")),
                name="order_total_matches_subtotal_plus_shipping",
            ),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(
                condition=Q(unit_price__gte=0) & Q(line_total__gte=0),
                name="orderitem_amounts_non_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(
                condition=Q(line_total=F("unit_price") * F("quantity")),
                name="orderitem_line_total_matches",
            ),
        ),
    ]
