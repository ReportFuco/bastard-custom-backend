# Generated manually

from django.db import migrations, models


def empty_phone_numbers_to_null(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.filter(phone_number="").update(phone_number=None)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_direccion_numero"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(blank=True, default=None, max_length=11, null=True, unique=True),
        ),
        migrations.RunPython(empty_phone_numbers_to_null, migrations.RunPython.noop),
    ]
