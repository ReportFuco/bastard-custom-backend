from django.db import models
from django.utils import timezone


class FranjaPromocional(models.Model):
    titulo = models.CharField(max_length=120)
    mensaje = models.CharField(max_length=255)
    etiqueta_cta = models.CharField(max_length=60, blank=True)
    url_cta = models.CharField(max_length=255, blank=True)
    color_fondo = models.CharField(max_length=7, default="#CAFD00")
    color_texto = models.CharField(max_length=7, default="#1A2200")
    activa = models.BooleanField(default=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    prioridad = models.PositiveIntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Franja promocional"
        verbose_name_plural = "Franjas promocionales"
        ordering = ("-prioridad", "-actualizado_en")

    def __str__(self) -> str:
        return self.titulo

    @property
    def esta_vigente(self) -> bool:
        ahora = timezone.now()
        if self.fecha_inicio and ahora < self.fecha_inicio:
            return False
        if self.fecha_fin and ahora > self.fecha_fin:
            return False
        return self.activa
