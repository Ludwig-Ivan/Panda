# tests/test_salud_y_seguridad.py
"""Criterios de HU-75: /health 200, /ready 503 hasta cargar, /v1/* sin X-API-Key → 401, límite de tamaño."""

import threading

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

from .conftest import CLAVE, esperar_listo, imagen_bytes


def test_health_siempre_responde(cliente):
    assert cliente.get("/health").json() == {"status": "ok"}


def test_ready_responde_503_mientras_carga_y_200_al_terminar(settings, monkeypatch):
    liberar = threading.Event()

    def fabrica_lenta(_settings):
        def _cargar():
            liberar.wait(5)
            from app.vision.estimador import EstimadorFalso

            return EstimadorFalso()

        return _cargar

    monkeypatch.setattr("app.main._fabrica_vision", fabrica_lenta)
    with TestClient(create_app(settings)) as c:
        assert c.get("/health").status_code == 200
        r = c.get("/ready")
        assert r.status_code == 503 and r.json()["componentes"]["vision"] == "cargando"
        foto = {"foto": ("a.jpg", imagen_bytes(), "image/jpeg")}
        assert c.post("/v1/vision/estimar", files=foto, headers={"X-API-Key": CLAVE}).status_code == 503
        liberar.set()
        esperar_listo(c)


def test_ready_queda_en_503_si_la_carga_falla(settings, monkeypatch):
    def fabrica_rota(_settings):
        def _cargar():
            raise RuntimeError("SHA-256 no coincide")

        return _cargar

    monkeypatch.setattr("app.main._fabrica_vision", fabrica_rota)
    with TestClient(create_app(settings)) as c:
        for _ in range(200):
            if c.get("/ready").json()["componentes"].get("vision") == "error":
                break
        r = c.get("/ready")
        assert r.status_code == 503 and r.json()["componentes"]["vision"] == "error"
        assert "SHA" not in r.text  # el detalle va a los logs, no a la respuesta


def test_rutas_v1_sin_clave_responden_401(cliente):
    assert cliente.get("/v1/actividad/catalogo?edad=30").status_code == 401
    r = cliente.post("/v1/vision/estimar", files={"foto": ("a.jpg", imagen_bytes(), "image/jpeg")})
    assert r.status_code == 401 and r.json()["error"]["code"] == "UNAUTHORIZED"


def test_clave_incorrecta_responde_401(cliente):
    assert cliente.get("/v1/actividad/catalogo?edad=30", headers={"X-API-Key": "otra"}).status_code == 401


def test_acepta_cualquiera_de_las_claves_configuradas(cliente):
    for clave in (CLAVE, "clave-anterior"):  # permite rotar sin cortar el servicio
        assert cliente.get("/v1/actividad/catalogo?edad=30", headers={"X-API-Key": clave}).status_code == 200


def test_sin_claves_configuradas_todo_v1_queda_cerrado(tmp_path):
    with TestClient(create_app(Settings(api_keys=[], modelo="falso", modelo_dir=tmp_path))) as c:
        esperar_listo(c)
        assert c.get("/v1/actividad/catalogo?edad=30", headers={"X-API-Key": ""}).status_code == 401


def test_peticion_mayor_al_limite_se_rechaza_antes_de_leerla(cliente, auth):
    enorme = b"\xff\xd8\xff" + b"0" * (11 * 1024 * 1024)
    r = cliente.post("/v1/vision/estimar", files={"foto": ("a.jpg", enorme, "image/jpeg")}, headers=auth)
    assert r.status_code == 413 and r.json()["error"]["code"] == "PAYLOAD_TOO_LARGE"


def test_limite_tambien_aplica_sin_content_length(cliente, auth):
    def trozos():
        for _ in range(12):
            yield b"0" * (1024 * 1024)

    r = cliente.post(
        "/v1/vision/estimar", content=trozos(), headers={**auth, "Content-Type": "multipart/form-data; boundary=x"}
    )
    assert r.status_code == 413


def test_la_documentacion_openapi_lista_las_rutas(cliente):
    rutas = cliente.get("/openapi.json").json()["paths"]
    assert {"/health", "/ready", "/v1/vision/estimar", "/v1/actividad/catalogo", "/v1/actividad/calcular"} <= set(rutas)


def test_demo_sirve_la_pagina_sin_clave_y_se_puede_apagar(cliente):
    r = cliente.get("/demo")
    assert r.status_code == 200 and "text/html" in r.headers["content-type"]
    assert "/v1/vision/estimar" in r.text  # la página usa los mismos endpoints protegidos


def test_demo_apagado_responde_404():
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import create_app

    app = create_app(Settings(api_keys=["x"], modelo="falso", demo=False), cargar=False)
    with TestClient(app) as c:
        assert c.get("/demo").status_code == 404
