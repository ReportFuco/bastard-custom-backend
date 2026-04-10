# Generated manually

from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_user_phone_number"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="direccion",
            constraint=models.UniqueConstraint(
                fields=("user",),
                condition=Q(is_default=True),
                name="uniq_default_direccion_per_user",
            ),
        ),
    ]
