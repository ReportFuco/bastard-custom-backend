# Generated manually

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0003_alter_inventoryitem_options"),
        ("users", "0003_direccion_single_default_constraint"),
    ]

    operations = [
        migrations.RenameField(
            model_name="inventoryitem",
            old_name="product",
            new_name="producto",
        ),
        migrations.RenameField(
            model_name="inventoryitem",
            old_name="available_quantity",
            new_name="cantidad_disponible",
        ),
        migrations.RenameField(
            model_name="inventoryitem",
            old_name="reserved_quantity",
            new_name="cantidad_reservada",
        ),
        migrations.RenameField(
            model_name="inventoryitem",
            old_name="updated_at",
            new_name="actualizado_en",
        ),
        migrations.AlterField(
            model_name="inventoryitem",
            name="producto",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="item_inventario",
                to="products.producto",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="inventoryitem",
            name="inventory_quantities_non_negative",
        ),
        migrations.AddConstraint(
            model_name="inventoryitem",
            constraint=models.CheckConstraint(
                condition=models.Q(("cantidad_disponible__gte", 0), ("cantidad_reservada__gte", 0)),
                name="cantidades_inventario_no_negativas",
            ),
        ),
        migrations.CreateModel(
            name="MovimientoInventario",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("entrada", "Entrada"),
                            ("salida", "Salida"),
                            ("ajuste", "Ajuste"),
                            ("reserva", "Reserva"),
                            ("liberacion", "Liberacion"),
                        ],
                        max_length=20,
                    ),
                ),
                ("cantidad", models.PositiveIntegerField()),
                ("cantidad_anterior", models.PositiveIntegerField()),
                ("cantidad_posterior", models.PositiveIntegerField()),
                ("motivo", models.CharField(blank=True, max_length=255)),
                ("referencia", models.CharField(blank=True, max_length=100)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                (
                    "creado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="movimientos_inventario_creados",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "item_inventario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="movimientos",
                        to="inventory.inventoryitem",
                    ),
                ),
            ],
            options={
                "verbose_name": "Movimiento de inventario",
                "verbose_name_plural": "Movimientos de inventario",
                "ordering": ("-creado_en",),
            },
        ),
        migrations.AddConstraint(
            model_name="movimientoinventario",
            constraint=models.CheckConstraint(
                condition=models.Q(("cantidad__gt", 0)),
                name="movimiento_inventario_cantidad_positiva",
            ),
        ),
    ]
