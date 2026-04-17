from django.apps import AppConfig


class InventoryConfig(AppConfig):
    name = 'inventory'
    verbose_name = "Inventario"

    def ready(self):
        from . import signals  # noqa: F401
