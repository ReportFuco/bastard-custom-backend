from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from users.phone import normalize_chile_phone_number


class InventoryItem(models.Model):
    producto = models.OneToOneField(
        "products.Producto",
        on_delete=models.CASCADE,
        related_name="item_inventario",
    )
    cantidad_disponible = models.PositiveIntegerField(default=0)
    cantidad_reservada = models.PositiveIntegerField(default=0)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item de inventario"
        verbose_name_plural = "Items de inventario"
        constraints = [
            models.CheckConstraint(
                condition=Q(cantidad_disponible__gte=0) & Q(cantidad_reservada__gte=0),
                name="cantidades_inventario_no_negativas",
            ),
        ]

    @property
    def cantidad_total(self) -> int:
        return self.cantidad_disponible + self.cantidad_reservada

    @property
    def en_stock(self) -> bool:
        return self.cantidad_disponible > 0

    def __str__(self) -> str:
        return f"{self.producto.nombre} - {self.cantidad_disponible} disponibles"


class MovimientoInventario(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = "entrada", "Entrada"
        SALIDA = "salida", "Salida"
        AJUSTE = "ajuste", "Ajuste"
        RESERVA = "reserva", "Reserva"
        LIBERACION = "liberacion", "Liberacion"

    item_inventario = models.ForeignKey(
        "inventory.InventoryItem",
        on_delete=models.CASCADE,
        related_name="movimientos",
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    cantidad = models.PositiveIntegerField()
    cantidad_anterior = models.PositiveIntegerField()
    cantidad_posterior = models.PositiveIntegerField()
    motivo = models.CharField(max_length=255, blank=True)
    referencia = models.CharField(max_length=100, blank=True)
    creado_por = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos_inventario_creados",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Movimientos de inventario"
        ordering = ("-creado_en",)
        constraints = [
            models.CheckConstraint(
                condition=Q(cantidad__gt=0),
                name="movimiento_inventario_cantidad_positiva",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.item_inventario.producto.nombre} | {self.get_tipo_display()} | "
            f"{self.cantidad_anterior}->{self.cantidad_posterior}"
        )


class Proveedor(models.Model):
    nombre_proveedor = models.CharField(max_length=120, unique=True)
    contacto_proveedor = models.CharField(max_length=11)
    email_contacto = models.EmailField(unique=True)
    sitio_web = models.URLField(blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ("nombre_proveedor",)

    def __str__(self) -> str:
        return self.nombre_proveedor

    def clean(self):
        super().clean()
        errors = {}
        if self.latitud is not None and not (-90 <= self.latitud <= 90):
            errors["latitud"] = "La latitud debe estar entre -90 y 90."
        if self.longitud is not None and not (-180 <= self.longitud <= 180):
            errors["longitud"] = "La longitud debe estar entre -180 y 180."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.contacto_proveedor = normalize_chile_phone_number(self.contacto_proveedor)
        self.full_clean()
        return super().save(*args, **kwargs)


class ProductoProveedor(models.Model):
    producto = models.ForeignKey(
        "products.Producto",
        on_delete=models.CASCADE,
        related_name="proveedores",
    )
    proveedor = models.ForeignKey(
        "inventory.Proveedor",
        on_delete=models.CASCADE,
        related_name="productos",
    )
    codigo_proveedor = models.CharField(max_length=80, blank=True)
    costo_compra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tiempo_reposicion_dias = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto proveedor"
        verbose_name_plural = "Productos proveedores"
        ordering = ("producto__nombre", "proveedor__nombre_proveedor")
        constraints = [
            models.UniqueConstraint(
                fields=["producto", "proveedor"],
                name="producto_proveedor_unico",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.producto.nombre} - {self.proveedor.nombre_proveedor}"
