from django.db import models


class Categorias(models.Model):

    nombre = models.CharField(max_length=150)
    slug = models.CharField(max_length=150, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.nombre}"


class Producto(models.Model):
    
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(
        Categorias, 
        on_delete=models.PROTECT, 
        related_name="productos"
    )

    slug = models.CharField(max_length=255, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.nombre}"    


class ProductoImagen(models.Model):

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="imagenes"
    )
    imagen = models.ImageField(upload_to="productos/")
    principal = models.BooleanField(default=False)
    nombre = models.CharField(max_length=150)


class Color(models.Model):
    nombre = models.CharField(max_length=30)
    hex_code = models.CharField(
        max_length=7,
        help_text="Formato HEX, ej: #FF5733"
    )

    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ("nombre", "hex_code")

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
