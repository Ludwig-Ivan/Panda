# app/vision/esquemas.py
"""Contrato de salida de POST /v1/vision/estimar (ver docs/contrato-vision.md)."""

from typing import Literal

from pydantic import BaseModel, Field


class Nutriente(BaseModel):
    valor: float = Field(ge=0, description="Estimación puntual del modelo")
    min: float = Field(ge=0, description="valor × (1 − %MAE)")
    max: float = Field(ge=0, description="valor × (1 + %MAE)")
    unidad: Literal["kcal", "g"]
    pct_mae: float = Field(description="%MAE del test oficial usado para el rango")


class Nutrientes(BaseModel):
    calorias: Nutriente
    masa: Nutriente
    grasa: Nutriente
    carbohidrato: Nutriente
    proteina: Nutriente


class ModeloInfo(BaseModel):
    nombre: str
    version: str = Field(description="Primeros 12 caracteres del SHA-256 de best.pt")


class RespuestaVision(BaseModel):
    modelo: ModeloInfo
    nutrientes: Nutrientes
    avisos: list[str]
    latencia_ms: int
