# panda/dominio/recomendacion.py
from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from .calorias import redondear

FORMULA_VERSION = "met-neto-v1"


class Intensidad(StrEnum):
    LIGERA = "ligera"
    MODERADA = "moderada"
    VIGOROSA = "vigorosa"


class NivelActividad(StrEnum):
    SEDENTARIO = "sedentario"
    LIGERO = "ligero"
    MODERADO = "moderado"
    ALTO = "alto"


INTENSIDADES_PERMITIDAS: dict[NivelActividad, frozenset[Intensidad]] = {
    NivelActividad.SEDENTARIO: frozenset({Intensidad.LIGERA, Intensidad.MODERADA}),
    NivelActividad.LIGERO: frozenset({Intensidad.LIGERA, Intensidad.MODERADA}),
    NivelActividad.MODERADO: frozenset(Intensidad),
    NivelActividad.ALTO: frozenset(Intensidad),
}


@dataclass(frozen=True)
class ActividadCatalogo:
    id: int
    nombre: str
    met: float
    intensidad: Intensidad


@dataclass(frozen=True)
class ParametrosRecomendacion:
    max_continua_min: int = 90
    sesion_fraccion_min: int = 45
    max_total_min: int = 180
    max_actividades: int = 5
    minimo_deseado: int = 3


@dataclass(frozen=True)
class ActividadRecomendada:
    actividad: ActividadCatalogo
    duracion_min: int
    sesiones: int
    kcal_estimadas: int
    es_preferida: bool


@dataclass(frozen=True)
class Recomendacion:
    kcal_objetivo: int
    peso_kg: float
    formula_version: str
    actividades: tuple[ActividadRecomendada, ...]
    mensaje: str


class _ConSesiones(Protocol):
    @property
    def sesiones(self) -> int: ...   # property: acepta dataclasses frozen


def kcal_por_minuto(met: float, peso_kg: float) -> float:
    if met <= 1:
        raise ValueError("El MET debe ser mayor que 1 para el cálculo neto")
    if peso_kg <= 0:
        raise ValueError("El peso debe ser positivo")
    return (met - 1) * 3.5 * peso_kg / 200


def _multiplo_de_5(minutos: float) -> int:
    return max(5, math.ceil(round(minutos / 5, 6)) * 5)


def planificar(kcal: float, kpm: float, p: ParametrosRecomendacion) -> tuple[int, int] | None:
    """Devuelve (duración total, sesiones) o None si la actividad no es viable."""
    duracion = _multiplo_de_5(kcal / kpm)
    if duracion > p.max_total_min:
        return None
    sesiones = 1
    if duracion > p.max_continua_min:
        sesiones = math.ceil(duracion / p.sesion_fraccion_min)
        duracion = _multiplo_de_5(duracion / sesiones) * sesiones
        if duracion > p.max_total_min:
            return None
    return duracion, sesiones


def mensaje_para(actividades: Sequence[_ConSesiones], p: ParametrosRecomendacion = ParametrosRecomendacion()) -> str:
    """Texto neutral, sin culpa ni obligación (RN-04, RI-U-09)."""
    if not actividades:
        return "Hoy no encontramos actividades que encajen con tu perfil. Cualquier movimiento ligero suma."
    partes = ["Puedes elegir la opción que mejor se acomode a tu día."]
    if len(actividades) < p.minimo_deseado:
        partes.append("Encontramos pocas opciones adecuadas para tu perfil; cualquier movimiento suma.")
    if any(a.sesiones > 1 for a in actividades):
        partes.append("Las sesiones pueden repartirse en varios momentos.")
    return " ".join(partes)


def recomendar(
    kcal_objetivo: int,
    peso_kg: float,
    nivel: NivelActividad,
    catalogo: Iterable[ActividadCatalogo],
    preferidas: set[int],
    p: ParametrosRecomendacion = ParametrosRecomendacion(),
) -> Recomendacion:
    actividades: list[ActividadRecomendada] = []
    if kcal_objetivo > 0:
        permitidas = INTENSIDADES_PERMITIDAS[nivel]
        candidatas = sorted(
            (a for a in catalogo if a.intensidad in permitidas),
            key=lambda a: (a.id not in preferidas, a.met, a.nombre),
        )
        for actividad in candidatas:
            kpm = kcal_por_minuto(actividad.met, peso_kg)
            plan = planificar(kcal_objetivo, kpm, p)
            if plan is None:
                continue
            duracion, sesiones = plan
            actividades.append(
                ActividadRecomendada(actividad, duracion, sesiones, redondear(duracion * kpm), actividad.id in preferidas)
            )
            if len(actividades) == p.max_actividades:
                break
    return Recomendacion(kcal_objetivo, peso_kg, FORMULA_VERSION, tuple(actividades), mensaje_para(actividades, p))