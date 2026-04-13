# Generated manually

from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_direccion_single_default_constraint"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="direccion",
            name="uniq_default_direccion_per_user",
        ),
        migrations.RenameField(
            model_name="direccion",
            old_name="user",
            new_name="usuario",
        ),
        migrations.RenameField(
            model_name="direccion",
            old_name="label",
            new_name="etiqueta",
        ),
        migrations.RenameField(
            model_name="direccion",
            old_name="is_default",
            new_name="es_predeterminada",
        ),
        migrations.RenameField(
            model_name="direccion",
            old_name="created_at",
            new_name="creado_en",
        ),
        migrations.RenameField(
            model_name="direccion",
            old_name="updated_at",
            new_name="actualizado_en",
        ),
        migrations.AddConstraint(
            model_name="direccion",
            constraint=models.UniqueConstraint(
                fields=("usuario",),
                condition=Q(es_predeterminada=True),
                name="direccion_predeterminada_unica_por_usuario",
            ),
        ),
    ]
