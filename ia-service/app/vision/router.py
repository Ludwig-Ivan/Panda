# app/vision/router.py
"""POST /v1/vision/estimar (T-212, T-213)."""

import asyncio
import time
from typing import Annotated

from fastapi import APIRouter, Depends, File, Request, UploadFile

from ..config import Settings, get_settings
from ..errores import ArchivoMuyGrande, ModeloNoListo
from ..seguridad import requiere_api_key
from . import NUTRIENTES, UNIDADES
from .esquemas import ModeloInfo, Nutriente, Nutrientes, RespuestaVision
from .imagen import validar_y_limpiar
from .rango import AVISOS, rango

router = APIRouter(prefix="/v1/vision", tags=["Visión"], dependencies=[Depends(requiere_api_key)])

RESPUESTAS = {
    401: {"description": "Falta X-API-Key o no es válida"},
    413: {"description": "La foto pesa más de 10 MB"},
    415: {"description": "No es JPEG, PNG ni WebP (se revisa el contenido, no la extensión)"},
    422: {"description": "Resolución menor a 640×480 o campo `foto` ausente"},
    503: {"description": "El modelo todavía no está cargado"},
}


@router.post("/estimar", response_model=RespuestaVision, responses=RESPUESTAS)
async def estimar(
    request: Request, foto: Annotated[UploadFile, File()], settings: Annotated[Settings, Depends(get_settings)]
) -> RespuestaVision:
    estado = request.app.state.estado
    estimador, metricas = estado.obtener("vision"), estado.obtener("metricas")
    if estimador is None or metricas is None:
        raise ModeloNoListo()

    datos = await foto.read(settings.max_bytes + 1)  # nunca se lee más de 10 MB + 1 byte
    if len(datos) > settings.max_bytes:
        raise ArchivoMuyGrande()
    imagen = validar_y_limpiar(datos, settings.max_bytes, settings.min_lado_mayor, settings.min_lado_menor)
    del datos  # la foto original no se conserva

    inicio = time.monotonic()
    pred = await asyncio.to_thread(estimador.predecir, imagen)  # la inferencia no bloquea el event loop
    latencia = round((time.monotonic() - inicio) * 1000)

    nutrientes = {}
    for n in NUTRIENTES:
        valor = max(0.0, float(pred[n]))
        bajo, alto = rango(valor, metricas.pct_mae[n])
        nutrientes[n] = Nutriente(
            valor=round(valor, 1),
            min=round(bajo, 1),
            max=round(alto, 1),
            unidad=UNIDADES[n],
            pct_mae=round(metricas.pct_mae[n], 1),
        )
    return RespuestaVision(
        modelo=ModeloInfo(nombre=estimador.nombre, version=estimador.version),
        nutrientes=Nutrientes(**nutrientes),
        avisos=list(AVISOS),
        latencia_ms=latencia,
    )
