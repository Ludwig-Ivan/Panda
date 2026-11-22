"""Header Idempotency-Key en POST /estimaciones y POST /comidas (API §8)."""

import uuid
from collections.abc import Callable

from django.core.cache import cache
from rest_framework.response import Response

from .errores import ErrorValidacion

TTL_SEGUNDOS = 24 * 60 * 60


def con_idempotencia(request, ejecutar: Callable[[], Response]) -> Response:
    clave = request.headers.get("Idempotency-Key")
    if not clave:
        return ejecutar()
    try:
        uuid.UUID(clave)
    except ValueError as exc:
        raise ErrorValidacion(details=[{"field": "Idempotency-Key", "issue": "invalid_uuid"}]) from exc

    clave_cache = f"idem:{request.user.pk}:{clave}"
    if guardada := cache.get(clave_cache):
        return Response(guardada["data"], status=guardada["status"], headers=guardada["headers"])

    respuesta = ejecutar()
    if 200 <= respuesta.status_code < 300:
        headers = {k: respuesta[k] for k in ("Location",) if respuesta.has_header(k)}
        cache.set(
            clave_cache, {"data": respuesta.data, "status": respuesta.status_code, "headers": headers}, TTL_SEGUNDOS
        )
    return respuesta
