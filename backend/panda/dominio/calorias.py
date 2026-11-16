from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum


class FuenteKcal(StrEnum):
    CATALOGO = "catalogo"
    ESTIMADO_IA = "estimado_ia"
    USUARIO = "usuario"


@dataclass(frozen=True)
class ParametrosRango:
    base: float = 0.15
    pendiente: float = 0.30
    minimo: float = 0.15
    maximo: float = 0.45
    extra_estimado_ia: float = 0.15
    usuario: float = 0.10
    confianza_revision: float = 0.50


@dataclass(frozen=True)
class EntradaItem:
    gramos: float
    kcal_100g: float
    confianza: float | None
    fuente: FuenteKcal
    capturado_por_usuario: bool


@dataclass(frozen=True)
class ResultadoItem:
    kcal: int
    kcal_min: int
    kcal_max: int
    requiere_revision: bool = False


@dataclass(frozen=True)
class RangoKcal:
    total: int
    min: int
    max: int


def redondear(valor: float, multiplo: int = 1) -> int:
    """Redondeo 'half up' determinista (Python usa redondeo bancario con round())."""
    cociente = Decimal(str(valor)) / Decimal(multiplo)
    return int(cociente.quantize(Decimal("1"), rounding=ROUND_HALF_UP)) * multiplo


def kcal_por_porcion(gramos: float, kcal_100g: float) -> float:
    if gramos <= 0:
        raise ValueError("La porción debe ser mayor que 0 g")
    if kcal_100g < 0:
        raise ValueError("La densidad energética no puede ser negativa")
    return gramos * kcal_100g / 100


def factor_rango(entrada: EntradaItem, p: ParametrosRango = ParametrosRango()) -> float:
    if entrada.capturado_por_usuario:
        return p.usuario
    confianza = entrada.confianza if entrada.confianza is not None else 0.0
    f = min(max(p.base + p.pendiente * (1 - confianza), p.minimo), p.maximo)
    if entrada.fuente is FuenteKcal.ESTIMADO_IA:
        f += p.extra_estimado_ia
    return f


def calcular_item(entrada: EntradaItem, p: ParametrosRango = ParametrosRango()) -> ResultadoItem:
    kcal = redondear(kcal_por_porcion(entrada.gramos, entrada.kcal_100g))
    f = factor_rango(entrada, p)
    confianza_baja = (
        not entrada.capturado_por_usuario
        and entrada.confianza is not None
        and entrada.confianza < p.confianza_revision
    )
    return ResultadoItem(
        kcal=kcal,
        kcal_min=redondear(kcal * (1 - f)),
        kcal_max=redondear(kcal * (1 + f)),
        requiere_revision=entrada.fuente is FuenteKcal.ESTIMADO_IA or confianza_baja,
    )


def totalizar(items: Iterable[ResultadoItem]) -> RangoKcal:
    lista = list(items)
    return RangoKcal(
        total=redondear(sum(i.kcal for i in lista), 10),
        min=redondear(sum(i.kcal_min for i in lista), 10),
        max=redondear(sum(i.kcal_max for i in lista), 10),
    )