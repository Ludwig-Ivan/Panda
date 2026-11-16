from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex, OpClass
from django.db import models
from django.db.models import Q

from panda.dominio.texto import normalizar


class FuenteAlimento(models.TextChoices):
    FDC = "fdc", "USDA FoodData Central"
    CURADO = "curado", "Curado por el equipo"


class Intensidad(models.TextChoices):
    LIGERA = "ligera", "Ligera"
    MODERADA = "moderada", "Moderada"
    VIGOROSA = "vigorosa", "Vigorosa"


class Alimento(models.Model):
    nombre = models.CharField(max_length=100)
    nombre_normalizado = models.CharField(max_length=100, editable=False)
    alias = ArrayField(models.CharField(max_length=100), default=list, blank=True)
    kcal_100g = models.DecimalField(max_digits=6, decimal_places=2)
    porcion_tipica_g = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    fuente = models.CharField(max_length=10, choices=FuenteAlimento.choices)
    fuente_ref = models.CharField(max_length=100, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alimentos"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(fields=["nombre_normalizado"], name="uq_alimentos_nombre_normalizado"),
            models.CheckConstraint(condition=Q(kcal_100g__gte=0, kcal_100g__lte=900), name="ck_alimentos_kcal"),
            models.CheckConstraint(
                condition=Q(porcion_tipica_g__isnull=True) | Q(porcion_tipica_g__gte=1, porcion_tipica_g__lte=2000),
                name="ck_alimentos_porcion",
            ),
            models.CheckConstraint(condition=Q(fuente__in=FuenteAlimento.values), name="ck_alimentos_fuente"),
        ]
        indexes = [
            GinIndex(OpClass("nombre_normalizado", name="gin_trgm_ops"), name="idx_alimentos_nombre_trgm"),
            GinIndex(fields=["alias"], name="idx_alimentos_alias"),
        ]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.nombre_normalizado = normalizar(self.nombre)
        self.alias = sorted({normalizar(a) for a in self.alias if a and a.strip()})
        super().save(*args, **kwargs)


class Actividad(models.Model):
    codigo_compendium = models.CharField(max_length=10)
    nombre = models.CharField(max_length=80)
    met = models.DecimalField(max_digits=4, decimal_places=1)
    intensidad = models.CharField(max_length=10, choices=Intensidad.choices)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "actividades"
        verbose_name_plural = "actividades"
        ordering = ["met"]
        constraints = [
            models.UniqueConstraint(fields=["codigo_compendium"], name="uq_actividades_codigo"),
            models.CheckConstraint(condition=Q(met__gt=1, met__lte=20), name="ck_actividades_met"),
            models.CheckConstraint(
                condition=(
                    Q(intensidad="ligera", met__lt=3)
                    | Q(intensidad="moderada", met__gte=3, met__lt=6)
                    | Q(intensidad="vigorosa", met__gte=6)
                ),
                name="ck_actividades_intensidad",
            ),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.met} MET)"