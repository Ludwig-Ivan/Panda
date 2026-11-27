# app/salud.py
"""/health (proceso vivo) y /ready (modelos cargados). Sin autenticación: los usa la plataforma (T-204)."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Salud"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/ready", responses={503: {"description": "Algún modelo sigue cargando o falló"}})
def ready(request: Request) -> JSONResponse:
    estado = request.app.state.estado
    cuerpo = {"status": "ok" if estado.listo else "no_listo", "componentes": estado.resumen()}
    return JSONResponse(cuerpo, status_code=200 if estado.listo else 503)
