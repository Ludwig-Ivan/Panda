# tests/conftest.py
"""Fixtures. Por defecto se usa el EstimadorFalso: la CI corre sin red, sin GPU y sin pesos (criterio de HU-75)."""

import io
import time

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings
from app.main import create_app

CLAVE = "clave-de-prueba"


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(api_keys=[CLAVE, "clave-anterior"], modelo="falso", modelo_dir=tmp_path / "modelos")


def esperar_listo(cliente: TestClient, segundos: float = 10) -> None:
    limite = time.monotonic() + segundos
    while (r := cliente.get("/ready")).status_code != 200:
        if "error" in r.json()["componentes"].values() or time.monotonic() > limite:
            raise AssertionError(f"/ready no llegó a 200: {r.json()}")
        time.sleep(0.02)


@pytest.fixture
def cliente(settings):
    with TestClient(create_app(settings)) as c:
        esperar_listo(c)
        yield c


@pytest.fixture
def auth() -> dict:
    return {"X-API-Key": CLAVE}


def imagen_bytes(ancho=800, alto=600, formato="JPEG", exif: bytes | None = None, color=(200, 120, 40)) -> bytes:
    buffer = io.BytesIO()
    extra = {"exif": exif} if exif else {}
    Image.new("RGB", (ancho, alto), color).save(buffer, formato, **extra)
    return buffer.getvalue()
