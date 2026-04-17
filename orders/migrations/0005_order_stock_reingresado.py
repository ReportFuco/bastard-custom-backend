# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0004_remove_order_shipping_address_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="stock_reingresado",
            field=models.BooleanField(default=False),
        ),
    ]
