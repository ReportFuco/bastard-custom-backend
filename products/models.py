from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Categorias(models.Model):

    nombre = models.CharField(max_length=150)
    slug = models.CharField(max_length=150, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self) -> str:
        return f"{self.nombre}"


class Subcategoria(models.Model):
    categoria = models.ForeignKey(
        Categorias,
        on_delete=models.CASCADE,
        related_name="subcategorias",
    )
    nombre = models.CharField(max_length=150)
    slug = models.CharField(max_length=150, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ("categoria", "nombre")
        ordering = ("nombre",)
        verbose_name = "Subcategoria"
        verbose_name_plural = "Subcategorias"

    def __str__(self) -> str:
        return f"{self.categoria.nombre} / {self.nombre}"


class Marca(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    slug = models.CharField(max_length=150, unique=True)
    pais_origen = models.CharField(max_length=120, null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ("nombre",)

    def __str__(self) -> str:
        return self.nombre


class Producto(models.Model):
    
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(
        Categorias, 
        on_delete=models.PROTECT, 
        related_name="productos"
    )
    marca = models.ForeignKey(
        Marca,
        on_delete=models.PROTECT,
        related_name="productos",
        null=True,
        blank=True,
    )
    subcategoria = models.ForeignKey(
        Subcategoria,
        on_delete=models.PROTECT,
        related_name="productos",
        null=True,
        blank=True,
    )

    slug = models.CharField(max_length=255, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, null=True, blank=True)
    vistas = models.PositiveIntegerField(default=0, editable=False)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self) -> str:
        return f"{self.nombre}"

    @property
    def precio_vigente(self):
        if not hasattr(self, "precio_config"):
            return self.precio
        return self.precio_config.precio_final

    def clean(self):
        super().clean()
        if self.subcategoria and self.subcategoria.categoria_id != self.categoria_id:
            raise ValidationError(
                {
                    "subcategoria": "La subcategoria debe pertenecer a la categoria seleccionada."
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class TablaNutricional(models.Model):
    producto = models.OneToOneField(
        Producto,
        on_delete=models.CASCADE,
        related_name="tabla_nutricional",
    )
    porcion = models.CharField(max_length=80, blank=True)
    energia_kcal = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    proteinas_g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    grasas_totales_g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    grasas_saturadas_g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    carbohidratos_g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    azucares_g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    fibra_g = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    sodio_mg = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tabla nutricional"
        verbose_name_plural = "Tablas nutricionales"

    def __str__(self) -> str:
        return f"Tabla nutricional - {self.producto.nombre}"

    def clean(self):
        super().clean()
        campos_no_negativos = [
            "energia_kcal",
            "proteinas_g",
            "grasas_totales_g",
            "grasas_saturadas_g",
            "carbohidratos_g",
            "azucares_g",
            "fibra_g",
            "sodio_mg",
        ]
        errores = {}
        for campo in campos_no_negativos:
            valor = getattr(self, campo)
            if valor is not None and valor < 0:
                errores[campo] = "Este valor no puede ser negativo."
        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class PrecioProducto(models.Model):
    class Moneda(models.TextChoices):
        CLP = "CLP", "Peso chileno"
        USD = "USD", "Dolar"

    producto = models.OneToOneField(
        Producto,
        on_delete=models.CASCADE,
        related_name="precio_config",
    )
    precio_lista = models.DecimalField(max_digits=10, decimal_places=2)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    moneda = models.CharField(max_length=3, choices=Moneda.choices, default=Moneda.CLP)
    activo = models.BooleanField(default=True)
    vigencia_desde = models.DateTimeField(null=True, blank=True)
    vigencia_hasta = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Precio"
        verbose_name_plural = "Precios"

    def __str__(self) -> str:
        return f"{self.producto.nombre} - {self.precio_final} {self.moneda}"

    @property
    def vigente(self) -> bool:
        now = timezone.now()
        if self.vigencia_desde and now < self.vigencia_desde:
            return False
        if self.vigencia_hasta and now > self.vigencia_hasta:
            return False
        return self.activo

    @property
    def precio_final(self):
        if self.vigente and self.precio_oferta is not None:
            return self.precio_oferta
        return self.precio_lista

    def clean(self):
        super().clean()
        if self.precio_oferta is not None and self.precio_oferta > self.precio_lista:
            raise ValidationError(
                {"precio_oferta": "El precio de oferta no puede ser mayor al precio de lista."}
            )
        if self.vigencia_desde and self.vigencia_hasta and self.vigencia_hasta < self.vigencia_desde:
            raise ValidationError(
                {"vigencia_hasta": "La vigencia hasta no puede ser anterior a vigencia desde."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        result = super().save(*args, **kwargs)
        self.producto.precio = Decimal(self.precio_final)
        self.producto.save(update_fields=["precio", "updated_at"])
        return result


class ProductoImagen(models.Model):

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="imagenes"
    )
    imagen = models.ImageField(upload_to="productos/")
    principal = models.BooleanField(default=False)
    nombre = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Imagen de producto"
        verbose_name_plural = "Imagenes de producto"
        constraints = [
            models.UniqueConstraint(
                fields=["producto"],
                condition=Q(principal=True),
                name="producto_una_imagen_principal",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.principal and self.producto_id:
            ProductoImagen.objects.filter(
                producto_id=self.producto_id,
                principal=True,
            ).exclude(pk=self.pk).update(principal=False)
        return super().save(*args, **kwargs)


class Color(models.Model):
    nombre = models.CharField(max_length=30)
    hex_code = models.CharField(
        max_length=7,
        help_text="Formato HEX, ej: #FF5733"
    )

    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ("nombre", "hex_code")
        verbose_name = "Color"
        verbose_name_plural = "Colores"

    def __str__(self):
        return f"{self.nombre} ({self.hex_code})"


class ProductoColor(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="variantes_color"
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        related_name="productos"
    )

    class Meta:
        unique_together = ("producto", "color")
        verbose_name = "Color de producto"
        verbose_name_plural = "Colores de producto"
