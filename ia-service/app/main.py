# app/main.py
"""Aplicación FastAPI del servicio de IA (T-204).

Al arrancar, el lifespan carga en segundo plano:
  1. compendios de actividad (CSV, instantáneo)
  2. métricas del test (test_metrics.json) para el rango ±%MAE
  3. modelo de visión: descarga y verifica best.pt, y lo carga (puede tardar decenas de segundos)
/health responde desde el primer momento; /ready responde 503 hasta que los tres están listos.

Se arranca con: uvicorn app.main:create_app --factory
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import salud
from .actividad import compendio as compendio_actividad
from .actividad.router import router as actividad_router
from .config import Settings, get_settings
from .errores import registrar_manejadores
from .estado import Estado
from .limite import LimiteTamano
from .vision.rango import Metricas
from .vision.router import router as vision_router

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("ia")


def _fabrica_vision(settings: Settings):
    if settings.modelo == "falso":
        from .vision.estimador import EstimadorFalso

        return EstimadorFalso
    from .vision.estimador import EstimadorSiglip
    from .vision.pesos import asegurar_pesos

    def _cargar():
        ruta = asegurar_pesos(settings.modelo_dir, settings.modelo_archivo, settings.modelo_sha256, settings.modelo_url)
        return EstimadorSiglip.desde_checkpoint(ruta, settings.dispositivo, settings.modelo_sha256 or "")

    return _cargar


def cargar_componentes(estado: Estado, settings: Settings, en_segundo_plano: bool = True) -> None:
    estado.cargar("compendios", lambda: compendio_actividad.cargar(settings.compendios_dir), en_segundo_plano=False)
    estado.cargar("metricas", lambda: Metricas.desde_archivo(settings.metricas_path), en_segundo_plano=False)
    estado.cargar("vision", _fabrica_vision(settings), en_segundo_plano=en_segundo_plano)


def create_app(settings: Settings | None = None, cargar: bool = True) -> FastAPI:
    settings = settings or get_settings()
    if not settings.api_keys:
        log.warning("IA_API_KEYS está vacío: todas las rutas /v1/* responderán 401")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if cargar:
            cargar_componentes(app.state.estado, settings)
        yield

    app = FastAPI(
        title="Panda · Servicio de IA",
        version="0.1.0",
        lifespan=lifespan,
        description="Estimación de nutrientes desde una foto y minutos de actividad. Solo para el backend.",
    )
    app.state.estado = Estado()
    app.dependency_overrides[get_settings] = lambda: settings
    app.add_middleware(LimiteTamano, max_bytes=settings.max_bytes + settings.margen_multipart)
    registrar_manejadores(app)
    app.include_router(salud.router)
    app.include_router(vision_router)
    app.include_router(actividad_router)
    if settings.demo:
        from .demo import router as demo_router

        app.include_router(demo_router)
    return app
