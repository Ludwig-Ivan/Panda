# app/config.py
"""Configuración del servicio. Todo sale de variables de entorno con prefijo IA_ (T-204)."""

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

RAIZ = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="IA_", env_file=".env", extra="ignore")

    # Seguridad (T-206)
    api_keys: Annotated[list[str], NoDecode] = Field(default_factory=list)
    max_bytes: int = 10 * 1024 * 1024  # 10 MB por foto, igual que el backend
    margen_multipart: int = 64 * 1024  # cabeceras del multipart

    # Modelo de visión (T-204, T-210)
    modelo: Literal["siglip", "falso"] = "siglip"
    modelo_url: str | None = None
    modelo_sha256: str | None = None
    modelo_dir: Path = Path("/modelos")
    modelo_archivo: str = "best.pt"
    metricas_path: Path = RAIZ / "modelo" / "test_metrics.json"
    dispositivo: Literal["auto", "cpu", "cuda"] = "auto"

    # Validación de la imagen (T-212); mismos mínimos que el backend
    min_lado_mayor: int = 640
    min_lado_menor: int = 480

    # Página de prueba /demo (solo desarrollo; en producción IA_DEMO=false)
    demo: bool = True

    # Actividad (T-220)
    compendios_dir: Path = RAIZ / "data"

    @field_validator("api_keys", mode="before")
    @classmethod
    def _separar_por_comas(cls, valor):
        if isinstance(valor, str):
            return [k.strip() for k in valor.split(",") if k.strip()]
        return valor

    @field_validator("modelo_sha256")
    @classmethod
    def _sha_en_minusculas(cls, valor):
        return valor.strip().lower() if valor else valor


@lru_cache
def get_settings() -> Settings:
    return Settings()
