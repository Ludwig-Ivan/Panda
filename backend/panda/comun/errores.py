"""Excepciones de negocio y manejador único de errores (API Specification §7)."""

import math

import sentry_sdk
import structlog
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    ParseError,
    PermissionDenied,
    Throttled,
    UnsupportedMediaType,
    ValidationError,
)
from rest_framework.response import Response

log = structlog.get_logger(__name__)


class ErrorPanda(APIException):
    """Base de los errores con código propio. El mensaje siempre es apto para el usuario."""

    status_code: int = status.HTTP_400_BAD_REQUEST  # anotado: las subclases usan otros códigos
    codigo: str = "BAD_REQUEST"
    mensaje: str = "La solicitud no es válida."

    def __init__(self, mensaje=None, *, details=None, retry_after=None, status_code=None):
        self.mensaje_usuario = mensaje or self.mensaje
        self.details = details or []
        self.retry_after = retry_after
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail=self.mensaje_usuario, code=self.codigo)


class SolicitudInvalida(ErrorPanda):
    codigo, mensaje = "BAD_REQUEST", "Los parámetros de la consulta no son válidos."


class ErrorValidacion(ErrorPanda):
    codigo, mensaje = "VALIDATION_ERROR", "Revisa los datos marcados e inténtalo de nuevo."


class ConfirmacionRequerida(ErrorPanda):
    codigo, mensaje = "CONFIRMATION_REQUIRED", "Confirma la eliminación para continuar."


class NoAutenticado(ErrorPanda):
    status_code, codigo, mensaje = 401, "UNAUTHORIZED", "Tu sesión expiró. Inicia sesión de nuevo."


class CredencialesInvalidas(ErrorPanda):
    status_code, codigo = 401, "INVALID_CREDENTIALS"
    mensaje = "El correo o la contraseña no son correctos. Revisa e inténtalo de nuevo."


class NoEncontrado(ErrorPanda):
    status_code, codigo, mensaje = 404, "NOT_FOUND", "No encontramos lo que buscas. Puede que se haya eliminado."


class EmailTomado(ErrorPanda):
    status_code, codigo = 409, "EMAIL_TAKEN"
    mensaje = "Ya existe una cuenta con ese correo. Inicia sesión o usa otro correo."


class PerfilIncompleto(ErrorPanda):
    status_code, codigo, mensaje = 409, "PROFILE_INCOMPLETE", "Completa tu perfil para calcular tus recomendaciones."


class ConsentimientoRequerido(ErrorPanda):
    status_code, codigo = 409, "CONSENT_REQUIRED"
    mensaje = "Necesitamos que aceptes la versión vigente de los avisos para continuar."


class UltimoItem(ErrorPanda):
    status_code, codigo = 409, "LAST_ITEM"
    mensaje = "Una comida guardada necesita al menos un alimento. Si quieres, elimina la comida completa."


class ArchivoMuyGrande(ErrorPanda):
    status_code, codigo, mensaje = 413, "PAYLOAD_TOO_LARGE", "La foto pesa más de 10MB. Elige otra o reduce su tamaño."


class FormatoNoSoportado(ErrorPanda):
    status_code, codigo = 415, "UNSUPPORTED_MEDIA_TYPE"
    mensaje = "Ese archivo no es una imagen compatible. Usa una foto JPG, PNG o WebP."


class EdadRequerida(ErrorPanda):
    status_code, codigo, mensaje = 422, "AGE_REQUIREMENT", "Panda está disponible solo para personas de 18 años o más."


class ImagenMuyPequena(ErrorPanda):
    status_code, codigo = 422, "IMAGE_TOO_SMALL"
    mensaje = "La foto es muy pequeña. Usa una imagen de al menos 640×480 píxeles."


class SinComidaDetectada(ErrorPanda):
    status_code, codigo = 422, "NO_FOOD_DETECTED"
    mensaje = "No pudimos reconocer comida en la foto. Intenta con otra imagen más cercana y bien iluminada."


class LimiteDiarioAlcanzado(ErrorPanda):
    status_code, codigo = 429, "DAILY_LIMIT_REACHED"
    mensaje = "Llegaste al límite de estimaciones de hoy. Puedes registrar tu comida manualmente."


class VisionNoDisponible(ErrorPanda):
    status_code, codigo = 503, "VISION_UNAVAILABLE"
    mensaje = "No pudimos analizar la foto en este momento. Intenta de nuevo o registra los alimentos manualmente."


# --- Manejador ------------------------------------------------------------


def a_camel(nombre: str) -> str:
    partes = nombre.split("_")
    return partes[0] + "".join(p.title() for p in partes[1:])


def aplanar_errores(detalle, ruta: str = "") -> list[dict]:
    """Convierte los errores anidados de DRF en una lista plana de {field, issue, message}."""
    salida: list[dict] = []
    if isinstance(detalle, dict):
        for campo, valor in detalle.items():
            nombre = campo if campo == "non_field_errors" else a_camel(str(campo))
            salida += aplanar_errores(valor, f"{ruta}.{nombre}" if ruta else nombre)
    elif isinstance(detalle, list):
        for i, valor in enumerate(detalle):
            salida += aplanar_errores(valor, f"{ruta}[{i}]" if isinstance(valor, dict | list) else ruta)
    else:
        salida.append({"field": ruta or None, "issue": getattr(detalle, "code", "invalid"), "message": str(detalle)})
    return salida


def _respuesta(status_code, codigo, mensaje, details, request_id, retry_after=None):
    headers = {"Retry-After": str(retry_after)} if retry_after else None
    cuerpo = {"error": {"code": codigo, "message": mensaje, "details": details, "requestId": request_id}}
    return Response(cuerpo, status=status_code, headers=headers)


def manejar_excepcion(exc, context):
    request = context.get("request")
    request_id = getattr(request, "request_id", "") if request else ""

    if isinstance(exc, Http404):
        exc = NotFound()

    if isinstance(exc, ErrorPanda):
        return _respuesta(exc.status_code, exc.codigo, exc.mensaje_usuario, exc.details, request_id, exc.retry_after)
    if isinstance(exc, ValidationError):
        return _respuesta(400, "VALIDATION_ERROR", ErrorValidacion.mensaje, aplanar_errores(exc.detail), request_id)
    if isinstance(exc, NotAuthenticated | AuthenticationFailed):
        return _respuesta(401, "UNAUTHORIZED", NoAutenticado.mensaje, [], request_id)
    if isinstance(exc, NotFound):
        return _respuesta(404, "NOT_FOUND", NoEncontrado.mensaje, [], request_id)
    if isinstance(exc, Throttled):
        espera = math.ceil(exc.wait or 60)
        return _respuesta(
            429,
            "RATE_LIMITED",
            "Hiciste muchas solicitudes seguidas. Espera un momento e inténtalo de nuevo.",
            [],
            request_id,
            espera,
        )
    if isinstance(exc, ParseError):
        return _respuesta(400, "BAD_REQUEST", "No pudimos leer la solicitud. Revisa el formato.", [], request_id)
    if isinstance(exc, UnsupportedMediaType):
        return _respuesta(415, "UNSUPPORTED_MEDIA_TYPE", FormatoNoSoportado.mensaje, [], request_id)
    if isinstance(exc, PermissionDenied):
        return _respuesta(403, "FORBIDDEN", "No tienes permiso para realizar esta acción.", [], request_id)
    if isinstance(exc, MethodNotAllowed):
        return _respuesta(405, "METHOD_NOT_ALLOWED", "Esta operación no está disponible.", [], request_id)
    if isinstance(exc, APIException):
        return _respuesta(exc.status_code, "BAD_REQUEST", ErrorPanda.mensaje, [], request_id)

    # Error no controlado: se registra y se responde sin detalles técnicos.
    sentry_sdk.capture_exception(exc)
    log.error("error_no_controlado", exc_info=exc)
    return _respuesta(
        500, "INTERNAL_ERROR", "Algo salió mal de nuestro lado. Inténtalo de nuevo en unos minutos.", [], request_id
    )
