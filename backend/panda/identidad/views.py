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

from panda.comun.errores import CredencialesInvalidas
from panda.comun.throttles import LoginRateThrottle, RegistroRateThrottle

from . import services
from .serializers import LoginSerializer, RegistroSerializer, RenovacionSerializer, SesionSerializer, UsuarioSerializer
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
