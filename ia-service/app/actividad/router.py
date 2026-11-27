# app/actividad/router.py
"""GET /v1/actividad/catalogo y POST /v1/actividad/calcular (T-222).

RN-01 a RN-03: los textos nunca sugieren comer menos ni compensar con restricción; solo informan el tiempo de
actividad equivalente, con avisos neutrales.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from ..errores import ModeloNoListo, NoEncontrado, ParametrosInvalidos
from ..seguridad import requiere_api_key
from . import calculo
from .compendio import Compendios
from .esquemas import ActividadSalida, CalculoEntrada, CalculoSalida, Catalogo

router = APIRouter(prefix="/v1/actividad", tags=["Actividad"], dependencies=[Depends(requiere_api_key)])

AVISO_GENERAL = "El tiempo es una estimación aproximada; cualquier movimiento suma."
AVISO_ESTIMADO = "Para esta actividad el valor de adulto es estimado (no está en el compendio de adultos)."
AVISO_VIGOROSA = "Actividad vigorosa: si no la practicas con regularidad, consúltalo antes con un médico."
AVISO_FRACCIONAR = "Puedes repartir el tiempo en varios momentos del día."


def _compendios(request: Request) -> Compendios:
    compendios = request.app.state.estado.obtener("compendios")
    if compendios is None:
        raise ModeloNoListo("Los compendios de actividad todavía no están cargados.")
    return compendios


@router.get("/catalogo", response_model=Catalogo)
def catalogo(
    request: Request,
    edad: Annotated[int, Query(ge=18, le=100)],
    categoria: Annotated[str | None, Query(max_length=40)] = None,
    neto: bool = True,
) -> Catalogo:
    comp = _compendios(request).para_edad(edad)
    actividades = [
        a
        for a in comp.actividades.values()
        if (categoria is None or a.categoria == categoria) and (not neto or a.met > 1.0)
    ]
    actividades.sort(key=lambda a: (a.met, a.actividad))  # de la más suave a la más intensa
    return Catalogo(
        compendio=comp.nombre,
        factor_o2=comp.factor_o2,
        actividades=[
            ActividadSalida(
                codigo=a.codigo, categoria=a.categoria, actividad=a.actividad, met=a.met, estimado=a.estimado
            )
            for a in actividades
        ],
    )


@router.post("/calcular", response_model=CalculoSalida)
def calcular(request: Request, entrada: CalculoEntrada) -> CalculoSalida:
    comp = _compendios(request).para_edad(entrada.edad)
    actividad = comp.actividades.get(entrada.codigo)
    if actividad is None:
        raise NoEncontrado("No existe una actividad con ese código.")
    try:
        tasa = calculo.kcal_por_minuto(actividad.met, entrada.peso_kg, entrada.edad, entrada.neto)
    except ValueError as exc:
        raise ParametrosInvalidos(str(exc), details=[{"field": "codigo", "issue": "met_sin_gasto_extra"}]) from exc
    total = calculo.redondear(entrada.kcal / tasa)

    avisos = [AVISO_GENERAL]
    if actividad.estimado and comp.factor_o2 == calculo.K_ADULTOS:
        avisos.append(AVISO_ESTIMADO)
    if actividad.met >= calculo.MET_VIGOROSO:
        avisos.append(AVISO_VIGOROSA)
    supera = total > calculo.LIMITE_CONTINUO_MIN
    if supera:
        avisos.append(AVISO_FRACCIONAR)

    return CalculoSalida(
        codigo=actividad.codigo,
        actividad=actividad.actividad,
        met=actividad.met,
        compendio=comp.nombre,
        neto=entrada.neto,
        kcal=entrada.kcal,
        kcal_por_min=round(tasa, 2),
        minutos=total,
        tiempo=calculo.texto_tiempo(total),
        supera_limite_continuo=supera,
        avisos=avisos,
    )
