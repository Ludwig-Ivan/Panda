import hashlib
import re
import time
import uuid

import structlog
from django.conf import settings

log = structlog.get_logger("panda.http")
_ID_VALIDO = re.compile(r"^[A-Za-z0-9\-]{1,64}$")


def _usuario_hash(request) -> str | None:
    usuario = getattr(request, "user", None)
    if usuario is None or not getattr(usuario, "is_authenticated", False):
        return None
    return hashlib.sha256(f"{usuario.pk}{settings.SECRET_KEY}".encode()).hexdigest()[:12]


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        entrante = request.headers.get("X-Request-Id", "")
        request_id = entrante if _ID_VALIDO.match(entrante) else uuid.uuid4().hex[:16]
        request.request_id = request_id
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        inicio = time.monotonic()
        response = self.get_response(request)
        response["X-Request-Id"] = request_id
        # Solo ruta, nunca query string ni cuerpo (RNF-SG-11)
        log.info(
            "http_request",
            metodo=request.method,
            ruta=request.path,
            status=response.status_code,
            ms=round((time.monotonic() - inicio) * 1000),
            usuario=_usuario_hash(request),
        )
        return response
