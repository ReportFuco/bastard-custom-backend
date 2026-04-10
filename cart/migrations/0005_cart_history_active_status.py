# Generated manually

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0004_merge_duplicate_carts_and_one_to_one_user"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="carrito",
            name="checked_out_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="carrito",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Activo"),
                    ("checked_out", "Comprado"),
                    ("abandoned", "Abandonado"),
                ],
                default="active",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="carrito",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="carritos",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name="carrito",
            constraint=models.UniqueConstraint(
                fields=("user",),
                condition=Q(status="active"),
                name="uniq_active_cart_per_user",
            ),
        ),
    ]
