# app/actividad/esquemas.py
"""Contrato de /v1/actividad/*. Límites iguales a los del perfil de Panda (API Specification §6)."""

from pydantic import BaseModel, Field


class ActividadSalida(BaseModel):
    codigo: str
    categoria: str
    actividad: str
    met: float
    estimado: bool = Field(description="El MET de adulto se estimó desde el MET60")


class Catalogo(BaseModel):
    compendio: str
    factor_o2: float
    actividades: list[ActividadSalida]


class CalculoEntrada(BaseModel):
    kcal: float = Field(gt=0, le=5000, description="Calorías de la comida (por ejemplo, las de /v1/vision/estimar)")
    peso_kg: float = Field(ge=30, le=300)
    edad: int = Field(ge=18, le=100)
    codigo: str = Field(min_length=1, max_length=10, description="Código de /v1/actividad/catalogo")
    neto: bool = Field(default=True, description="True = solo el gasto extra por la actividad (ADR)")


class CalculoSalida(BaseModel):
    codigo: str
    actividad: str
    met: float
    compendio: str
    neto: bool
    kcal: float
    kcal_por_min: float
    minutos: int
    tiempo: str
    supera_limite_continuo: bool
    avisos: list[str]
