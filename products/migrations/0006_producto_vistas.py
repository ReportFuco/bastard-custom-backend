from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0005_productoimagen_producto_una_imagen_principal"),
    ]

    operations = [
        migrations.AddField(
            model_name="producto",
            name="vistas",
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
    ]
