# app/seguridad.py
"""Autenticación servicio a servicio con X-API-Key (T-206). Solo el backend de Panda llama a /v1/*."""

import hmac
from typing import Annotated

from fastapi import Depends, Header

from .config import Settings, get_settings
from .errores import NoAutorizado


def requiere_api_key(
    settings: Annotated[Settings, Depends(get_settings)],
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    # Si no hay claves configuradas el servicio se cierra por completo: nunca queda abierto por error.
    if not x_api_key or not settings.api_keys:
        raise NoAutorizado()
    # compare_digest contra cada clave: tiempo constante, no filtra cuál coincidió
    if not any(hmac.compare_digest(x_api_key.encode(), k.encode()) for k in settings.api_keys):
        raise NoAutorizado()
