# panda/recomendacion/models.py
import uuid

from django.db import models
from django.db.models import Q


class Recomendacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comida = models.OneToOneField("comidas.Comida", on_delete=models.CASCADE, related_name="recomendacion")
    kcal_objetivo = models.IntegerField()
    peso_kg_usado = models.DecimalField(max_digits=5, decimal_places=2)
    formula_version = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recomendaciones"
        constraints = [
            models.CheckConstraint(condition=Q(kcal_objetivo__gte=0, kcal_objetivo__lte=5000), name="ck_recomendaciones_kcal"),
        ]


class RecomendacionItem(models.Model):
    recomendacion = models.ForeignKey(Recomendacion, on_delete=models.CASCADE, related_name="items")
    actividad = models.ForeignKey("catalogos.Actividad", on_delete=models.PROTECT, related_name="+")
    orden = models.SmallIntegerField()
    duracion_min = models.SmallIntegerField()
    sesiones = models.SmallIntegerField(default=1)
    kcal_estimadas = models.IntegerField()
    es_preferida = models.BooleanField(default=False)

    class Meta:
        db_table = "recomendacion_items"
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(fields=["recomendacion", "orden"], name="uq_recomendacion_items_orden"),
            models.CheckConstraint(condition=Q(duracion_min__gte=5, duracion_min__lte=180), name="ck_recomendacion_items_duracion"),
            models.CheckConstraint(condition=Q(sesiones__gte=1, sesiones__lte=4), name="ck_recomendacion_items_sesiones"),
        ]