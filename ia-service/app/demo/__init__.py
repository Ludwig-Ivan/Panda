# app/demo/__init__.py
"""GET /demo: página para probar el servicio a mano (foto → nutrientes → actividad), como las secciones 10-12
del notebook comida.ipynb. No es la app: la app la hace el frontend. Se apaga con IA_DEMO=false.

La página no expone nada nuevo: llama a los mismos endpoints /v1/* y necesita la X-API-Key igual que el backend.
"""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

HTML = Path(__file__).with_name("demo.html")

router = APIRouter(tags=["Demo"])


@router.get("/demo", response_class=HTMLResponse, include_in_schema=False)
def demo() -> HTMLResponse:
    return HTMLResponse(HTML.read_text(encoding="utf-8"))
