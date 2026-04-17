# Generated manually

from django.db import migrations


def create_missing_inventory_items(apps, schema_editor):
    Producto = apps.get_model("products", "Producto")
    InventoryItem = apps.get_model("inventory", "InventoryItem")

    existing_product_ids = set(InventoryItem.objects.values_list("producto_id", flat=True))
    missing_items = [
        InventoryItem(producto_id=producto_id)
        for producto_id in Producto.objects.values_list("id", flat=True)
        if producto_id not in existing_product_ids
    ]
    InventoryItem.objects.bulk_create(missing_items)


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0006_proveedor_direccion_proveedor_latitud_and_more"),
        ("products", "0008_alter_producto_description"),
    ]

    operations = [
        migrations.RunPython(create_missing_inventory_items, migrations.RunPython.noop),
    ]
