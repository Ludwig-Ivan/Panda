# app/errores.py
"""Errores con el mismo formato que la API de Panda: {"error": {"code", "message", "details"}}."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErrorIA(Exception):
    status_code = 400
    code = "BAD_REQUEST"
    message = "La solicitud no es válida."

    def __init__(self, message: str | None = None, details: list | None = None):
        self.message = message or self.message
        self.details = details or []
        super().__init__(self.message)


class NoAutorizado(ErrorIA):
    status_code, code, message = 401, "UNAUTHORIZED", "Falta el header X-API-Key o no es válido."


class NoEncontrado(ErrorIA):
    status_code, code, message = 404, "NOT_FOUND", "No existe el recurso solicitado."


class ArchivoMuyGrande(ErrorIA):
    status_code, code, message = 413, "PAYLOAD_TOO_LARGE", "La foto pesa más de 10 MB."


class FormatoNoSoportado(ErrorIA):
    status_code, code, message = 415, "UNSUPPORTED_MEDIA_TYPE", "La imagen debe ser JPEG, PNG o WebP."


class ImagenMuyPequena(ErrorIA):
    status_code, code = 422, "IMAGE_TOO_SMALL"
    message = "La foto es muy pequeña. Usa una imagen de al menos 640×480 píxeles."


class ParametrosInvalidos(ErrorIA):
    status_code, code, message = 422, "VALIDATION_ERROR", "Revisa los datos enviados."


class ModeloNoListo(ErrorIA):
    status_code, code, message = 503, "MODEL_NOT_READY", "El modelo todavía no está cargado."


def _cuerpo(code: str, message: str, details: list) -> dict:
    return {"error": {"code": code, "message": message, "details": details}}


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(ErrorIA)
    async def _error_ia(_: Request, exc: ErrorIA):
        return JSONResponse(_cuerpo(exc.code, exc.message, exc.details), status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def _validacion(_: Request, exc: RequestValidationError):
        details = [
            {"field": ".".join(str(p) for p in e["loc"][1:]) or None, "issue": e["type"], "message": e["msg"]}
            for e in exc.errors()
        ]
        return JSONResponse(_cuerpo("VALIDATION_ERROR", ParametrosInvalidos.message, details), status_code=422)

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException):
        codigos = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}
        return JSONResponse(
            _cuerpo(codigos.get(exc.status_code, "BAD_REQUEST"), str(exc.detail), []), status_code=exc.status_code
        )
