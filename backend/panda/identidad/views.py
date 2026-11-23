import contextlib

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from panda.comun.errores import CredencialesInvalidas, NoEncontrado
from panda.comun.throttles import LoginRateThrottle, RegistroRateThrottle

from . import services
from .models import Consentimiento, Perfil, PreferenciaActividad
from .serializers import (
    ConsentimientosEntradaSerializer,
    EstadoConsentimientosSerializer,
    LoginSerializer,
    PerfilSerializer,
    PreferenciasSerializer,
    RegistroSerializer,
    RenovacionSerializer,
    SesionSerializer,
    UsuarioSerializer,
)
from .tokens import borrar_cookie_refresh, emitir_tokens, poner_cookie_refresh, rotar_refresh

EXPIRA_EN = int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())


def _respuesta_sesion(usuario, codigo):
    access, refresh = emitir_tokens(usuario)
    update_last_login(None, usuario)
    datos = {
        "access_token": access,
        "token_type": "Bearer",
        "expires_in": EXPIRA_EN,
        "usuario": UsuarioSerializer(usuario).data,
    }
    respuesta = Response(datos, status=codigo)
    poner_cookie_refresh(respuesta, refresh)
    return respuesta


class RegistroView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [RegistroRateThrottle]

    @extend_schema(request=RegistroSerializer, responses={201: SesionSerializer}, tags=["Auth"])
    def post(self, request):
        entrada = RegistroSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        usuario = services.registrar_usuario(**entrada.validated_data)
        return _respuesta_sesion(usuario, status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    @extend_schema(request=LoginSerializer, responses={200: SesionSerializer}, tags=["Auth"])
    def post(self, request):
        entrada = LoginSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        usuario = authenticate(
            request, email=entrada.validated_data["email"].strip().lower(), password=entrada.validated_data["password"]
        )
        if usuario is None or not usuario.is_active:
            raise CredencialesInvalidas()  # mensaje genérico: no dice si falló el correo o la contraseña
        return _respuesta_sesion(usuario, status.HTTP_200_OK)


class RefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(request=None, responses=RenovacionSerializer, tags=["Auth"])
    def post(self, request):
        _usuario, access, refresh = rotar_refresh(request.COOKIES.get(settings.AUTH_COOKIE["NOMBRE"]))
        respuesta = Response({"access_token": access, "token_type": "Bearer", "expires_in": EXPIRA_EN})
        poner_cookie_refresh(respuesta, refresh)
        return respuesta


class LogoutView(APIView):
    @extend_schema(request=None, responses={204: None}, tags=["Auth"])
    def post(self, request):
        raw = request.COOKIES.get(settings.AUTH_COOKIE["NOMBRE"])
        if raw:
            with contextlib.suppress(TokenError):  # un token inválido o vencido no impide cerrar sesión
                RefreshToken(raw).blacklist()
        respuesta = Response(status=status.HTTP_204_NO_CONTENT)
        borrar_cookie_refresh(respuesta)
        return respuesta


class UsuarioMeView(APIView):
    @extend_schema(responses=UsuarioSerializer, tags=["Cuenta"])
    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)

    @extend_schema(request=UsuarioSerializer, responses=UsuarioSerializer, tags=["Cuenta"])
    def patch(self, request):
        entrada = UsuarioSerializer(request.user, data=request.data, partial=True)
        entrada.is_valid(raise_exception=True)
        entrada.save()
        return Response(entrada.data)


class ConsentimientosView(APIView):
    def _estado(self, usuario):
        return {
            "vigentes": [{"tipo": t, "version": v} for t, v in services.versiones_vigentes().items()],
            "aceptados": list(Consentimiento.objects.filter(usuario=usuario).values("tipo", "version", "aceptado_at")),
            "pendientes": services.consentimientos_pendientes(usuario),
        }

    @extend_schema(responses=EstadoConsentimientosSerializer, tags=["Cuenta"])
    def get(self, request):
        return Response(self._estado(request.user))

    @extend_schema(request=ConsentimientosEntradaSerializer, responses=EstadoConsentimientosSerializer, tags=["Cuenta"])
    def post(self, request):
        entrada = ConsentimientosEntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        services.aceptar_consentimientos(request.user, entrada.validated_data["consentimientos"])
        return Response(self._estado(request.user))


class PerfilView(APIView):
    @extend_schema(responses=PerfilSerializer, tags=["Perfil"])
    def get(self, request):
        perfil = Perfil.objects.filter(usuario=request.user).first()
        if perfil is None:
            raise NoEncontrado("Aún no has capturado tu perfil.")
        return Response(PerfilSerializer(perfil).data)

    @extend_schema(request=PerfilSerializer, responses=PerfilSerializer, tags=["Perfil"])
    def put(self, request):
        entrada = PerfilSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        perfil, _ = Perfil.objects.update_or_create(usuario=request.user, defaults=entrada.validated_data)
        return Response(PerfilSerializer(perfil).data)


class PreferenciasView(APIView):
    @extend_schema(responses=PreferenciasSerializer, tags=["Perfil"])
    def get(self, request):
        ids = list(PreferenciaActividad.objects.filter(usuario=request.user).values_list("actividad_id", flat=True))
        return Response({"actividad_ids": ids})

    @extend_schema(request=PreferenciasSerializer, responses=PreferenciasSerializer, tags=["Perfil"])
    def put(self, request):
        entrada = PreferenciasSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        ids = services.reemplazar_preferencias(request.user, entrada.validated_data["actividad_ids"])
        return Response({"actividad_ids": ids})
