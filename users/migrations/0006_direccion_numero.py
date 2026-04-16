# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_alter_user_phone_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="direccion",
            name="numero",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
    ]
