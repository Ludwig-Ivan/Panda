import structlog
from django.conf import settings
from rest_framework_simplejwt.exceptions import TokenBackendError, TokenError
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from panda.comun.errores import NoAutenticado

from .models import Usuario

log = structlog.get_logger(__name__)
COOKIE = settings.AUTH_COOKIE


def emitir_tokens(usuario: Usuario) -> tuple[str, str]:
    refresh = RefreshToken.for_user(usuario)  # registra un OutstandingToken
    return str(refresh.access_token), str(refresh)


def poner_cookie_refresh(response, refresh: str) -> None:
    response.set_cookie(
        COOKIE["NOMBRE"],
        refresh,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=COOKIE["SECURE"],
        samesite=COOKIE["SAMESITE"],
        path=COOKIE["PATH"],
    )


def borrar_cookie_refresh(response) -> None:
    response.delete_cookie(COOKIE["NOMBRE"], path=COOKIE["PATH"], samesite=COOKIE["SAMESITE"])


def revocar_sesiones(usuario_id) -> None:
    vigentes = OutstandingToken.objects.filter(user_id=usuario_id, blacklistedtoken__isnull=True)
    BlacklistedToken.objects.bulk_create([BlacklistedToken(token=t) for t in vigentes], ignore_conflicts=True)


def _revocar_si_fue_reutilizado(raw: str) -> None:
    """Si alguien usa un refresh válido pero ya rotado, se asume robo y se cierran todas las sesiones."""
    try:
        payload = token_backend.decode(raw, verify=True)  # type: ignore[arg-type]  # el stub pide Token; acepta str
    except TokenBackendError:
        return
    if payload.get("token_type") != "refresh":
        return
    if BlacklistedToken.objects.filter(token__jti=payload.get("jti")).exists():
        log.warning("refresh_reutilizado")
        revocar_sesiones(payload.get("user_id"))


def rotar_refresh(raw: str | None) -> tuple[Usuario, str, str]:
    if not raw:
        raise NoAutenticado()
    try:
        actual = RefreshToken(raw)  # type: ignore[arg-type]  # verifica firma, expiración y blacklist
    except TokenError as exc:
        _revocar_si_fue_reutilizado(raw)
        raise NoAutenticado() from exc
    try:
        usuario = Usuario.objects.get(pk=actual["user_id"], is_active=True)
    except Usuario.DoesNotExist as exc:
        raise NoAutenticado() from exc
    actual.blacklist()
    access, nuevo = emitir_tokens(usuario)
    return usuario, access, nuevo
