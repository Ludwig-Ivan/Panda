import uuid
from decimal import Decimal

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class EstadoComida(models.TextChoices):
    BORRADOR = "borrador", "Borrador"
    CONFIRMADA = "confirmada", "Confirmada"


class OrigenComida(models.TextChoices):
    FOTO = "foto", "Foto"
    MANUAL = "manual", "Manual"


class OrigenItem(models.TextChoices):
    IA = "ia", "IA"
    USUARIO = "usuario", "Usuario"


class FuenteKcal(models.TextChoices):
    CATALOGO = "catalogo", "Catálogo"
    ESTIMADO_IA = "estimado_ia", "Estimado por IA"
    USUARIO = "usuario", "Usuario"


class TipoCorreccion(models.TextChoices):
    AGREGAR = "agregar", "Agregar"
    EDITAR = "editar", "Editar"
    ELIMINAR = "eliminar", "Eliminar"


def ruta_foto(instancia, _nombre_original):
    return f"usuarios/{instancia.usuario_id}/comidas/{instancia.id}.webp"


class Comida(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comidas")
    estado = models.CharField(max_length=12, choices=EstadoComida.choices, default=EstadoComida.BORRADOR)
    origen = models.CharField(max_length=10, choices=OrigenComida.choices, default=OrigenComida.FOTO)
    consumida_at = models.DateTimeField(default=timezone.now)
    foto = models.FileField(upload_to=ruta_foto, max_length=200, null=True, blank=True)
    kcal_total = models.IntegerField(default=0)
    kcal_min = models.IntegerField(default=0)
    kcal_max = models.IntegerField(default=0)
    estimacion_original = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)
    proveedor_vision = models.CharField(max_length=50, null=True, blank=True)
    modelo_version = models.CharField(max_length=80, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comidas"
        constraints = [
            models.CheckConstraint(condition=Q(estado__in=EstadoComida.values), name="ck_comidas_estado"),
            models.CheckConstraint(condition=Q(origen__in=OrigenComida.values), name="ck_comidas_origen"),
            models.CheckConstraint(
                condition=Q(kcal_total__gte=0,
                            kcal_total__lte=5000,
                            kcal_min__lte=F("kcal_total"),
                            kcal_max__gte=F("kcal_total")),
                name="ck_comidas_kcal_rango",
            ),
            models.CheckConstraint(
                condition=Q(origen="manual") | Q(estimacion_original__isnull=False),
                name="ck_comidas_origen_foto",
            ),
        ]
        indexes = [
            models.Index(fields=["usuario", "-consumida_at"], name="idx_comidas_usuario_consumida"),
            models.Index(fields=["created_at"], condition=Q(estado="borrador"), name="idx_comidas_borrador_created"),
        ]


class ComidaItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comida = models.ForeignKey(Comida, on_delete=models.CASCADE, related_name="items")
    alimento = models.ForeignKey("catalogos.Alimento",
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=True,
                                 related_name="+")
    nombre = models.CharField(max_length=100)
    porcion_g = models.DecimalField(max_digits=6, decimal_places=1)
    kcal_100g = models.DecimalField(max_digits=6, decimal_places=2)
    kcal = models.IntegerField()
    kcal_min = models.IntegerField()
    kcal_max = models.IntegerField()
    confianza = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    origen = models.CharField(max_length=10, choices=OrigenItem.choices)
    fuente_kcal = models.CharField(max_length=12, choices=FuenteKcal.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comida_items"
        ordering = ["created_at"]
        constraints = [
            models.CheckConstraint(condition=Q(porcion_g__gte=1,
                                               porcion_g__lte=2000),
                                               name="ck_comida_items_porcion"),
            models.CheckConstraint(
                condition=Q(kcal__gte=0,
                            kcal_min__lte=F("kcal"),
                            kcal_max__gte=F("kcal")),
                            name="ck_comida_items_kcal"
            ),
            models.CheckConstraint(
                condition=Q(confianza__isnull=True) | Q(confianza__gte=0, confianza__lte=1),
                name="ck_comida_items_confianza"
            ),
            models.CheckConstraint(
                condition=Q(origen="usuario") | Q(confianza__isnull=False),
                name="ck_comida_items_origen_confianza"
            ),
            models.CheckConstraint(condition=Q(origen__in=OrigenItem.values),
                                   name="ck_comida_items_origen"),
            models.CheckConstraint(condition=Q(fuente_kcal__in=FuenteKcal.values),
                                   name="ck_comida_items_fuente_kcal"),
        ]

    @property
    def requiere_revision(self) -> bool:
        umbral = Decimal(str(settings.PANDA["ESTIMACION"]["CONFIANZA_REVISION"]))
        return self.fuente_kcal == FuenteKcal.ESTIMADO_IA or (self.confianza is not None and self.confianza < umbral)


class Correccion(models.Model):
    comida = models.ForeignKey(Comida, on_delete=models.CASCADE, related_name="correcciones")
    item_id = models.UUIDField(null=True, blank=True)  # sin FK: el item puede haberse eliminado
    tipo = models.CharField(max_length=10, choices=TipoCorreccion.choices)
    valor_anterior = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)
    valor_nuevo = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "correcciones"
        ordering = ["created_at"]
        constraints = [
            models.CheckConstraint(condition=Q(tipo__in=TipoCorreccion.values), name="ck_correcciones_tipo"),
            models.CheckConstraint(
                condition=(
                    Q(tipo="agregar", valor_anterior__isnull=True, valor_nuevo__isnull=False)
                    | Q(tipo="editar", valor_anterior__isnull=False, valor_nuevo__isnull=False)
                    | Q(tipo="eliminar", valor_anterior__isnull=False, valor_nuevo__isnull=True)
                ),
                name="ck_correcciones_valores",
            ),
        ]
        indexes = [models.Index(fields=["comida", "created_at"], name="idx_correcciones_comida")]
