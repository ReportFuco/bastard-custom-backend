# Generated manually to enforce one active cart per user.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Count


def merge_duplicate_carts(apps, schema_editor):
    Carrito = apps.get_model("cart", "Carrito")
    ItemCarrito = apps.get_model("cart", "ItemCarrito")

    duplicated_users = (
        Carrito.objects
        .values("user_id")
        .annotate(total=Count("id"))
        .filter(total__gt=1)
        .values_list("user_id", flat=True)
    )

    for user_id in duplicated_users:
        carts = list(
            Carrito.objects
            .filter(user_id=user_id)
            .order_by("-updated_at", "-id")
        )
        if len(carts) < 2:
            continue

        keep_cart = carts[0]
        duplicate_carts = carts[1:]

        for duplicate_cart in duplicate_carts:
            duplicate_items = ItemCarrito.objects.filter(carrito_id=duplicate_cart.id)

            for item in duplicate_items:
                existing_item = ItemCarrito.objects.filter(
                    carrito_id=keep_cart.id,
                    producto_id=item.producto_id,
                ).first()

                if existing_item:
                    existing_item.cantidad = existing_item.cantidad + item.cantidad
                    existing_item.save(update_fields=["cantidad"])
                    item.delete()
                    continue

                item.carrito_id = keep_cart.id
                item.save(update_fields=["carrito"])

            duplicate_cart.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0003_alter_itemcarrito_unique_together"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(merge_duplicate_carts, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="carrito",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="carrito",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
