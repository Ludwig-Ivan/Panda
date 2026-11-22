from __future__ import annotations

from enum import StrEnum

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

def kcal_por_minuto(met: float, peso_kg: float) -> float:
    if met <= 1:
        raise ValueError("El MET debe ser mayor que 1 para el cálculo neto")
    if peso_kg <= 0:
        raise ValueError("El peso debe ser positivo")
    return (met - 1) * 3.5 * peso_kg / 200
