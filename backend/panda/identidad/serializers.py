# panda/identidad/serializers.py
from decimal import Decimal

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from panda.comun.errores import ConsentimientoRequerido, EdadRequerida, EmailTomado

from . import services
from .models import Perfil, TipoConsentimiento, Usuario


class ConsentimientoEntradaSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=TipoConsentimiento.choices)
    version = serializers.CharField(max_length=20)


class RegistroSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(min_length=8, max_length=128, write_only=True, trim_whitespace=False)
    mayor_edad = serializers.BooleanField()
    consentimientos = ConsentimientoEntradaSerializer(many=True)

    def validate_email(self, valor):
        valor = valor.strip().lower()
        if Usuario.objects.filter(email=valor).exists():
            raise EmailTomado()
        return valor

    def validate(self, datos):
        if not datos["mayor_edad"]:
            raise EdadRequerida()
        aceptados = {(c["tipo"], c["version"]) for c in datos["consentimientos"]}
        if services.consentimientos_faltantes(aceptados):
            raise ConsentimientoRequerido(status_code=422)
        try:
            validate_password(datos["password"], user=Usuario(email=datos["email"]))
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return datos


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False, write_only=True)


class UsuarioSerializer(serializers.ModelSerializer):
    perfil_completo = serializers.SerializerMethodField()
    consentimientos_vigentes = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ["id", "email", "guardar_fotos", "perfil_completo", "consentimientos_vigentes"]
        read_only_fields = ["id", "email"]

    def get_perfil_completo(self, obj) -> bool:
        return Perfil.objects.filter(usuario=obj).exists()

    def get_consentimientos_vigentes(self, obj) -> bool:
        return not services.consentimientos_pendientes(obj)


class SesionSerializer(serializers.Serializer):
    """Solo para documentar la respuesta en OpenAPI."""

    access_token = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()
    usuario = UsuarioSerializer()


class PerfilSerializer(serializers.ModelSerializer):
    edad = serializers.IntegerField(min_value=18, max_value=100)
    peso_kg = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=Decimal("30"), max_value=Decimal("300")
    )
    estatura_cm = serializers.DecimalField(
        max_digits=5, decimal_places=1, min_value=Decimal("120"), max_value=Decimal("230")
    )

    class Meta:
        model = Perfil
        fields = ["edad", "sexo", "peso_kg", "estatura_cm", "nivel_actividad", "updated_at"]
        read_only_fields = ["updated_at"]


class ConsentimientosEntradaSerializer(serializers.Serializer):
    consentimientos = ConsentimientoEntradaSerializer(many=True, allow_empty=False)


class PreferenciasSerializer(serializers.Serializer):
    actividad_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), max_length=10, allow_empty=True)


class EliminarCuentaSerializer(serializers.Serializer):
    password = serializers.CharField(trim_whitespace=False, write_only=True)


class RenovacionSerializer(serializers.Serializer):
    """Solo para documentar POST /auth/refresh en OpenAPI."""

    access_token = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()


class ConsentimientoAceptadoSerializer(ConsentimientoEntradaSerializer):
    aceptado_at = serializers.DateTimeField()


class EstadoConsentimientosSerializer(serializers.Serializer):
    """Solo para documentar GET/POST /consentimientos en OpenAPI."""

    vigentes = ConsentimientoEntradaSerializer(many=True)
    aceptados = ConsentimientoAceptadoSerializer(many=True)
    pendientes = serializers.ListField(child=serializers.CharField())
