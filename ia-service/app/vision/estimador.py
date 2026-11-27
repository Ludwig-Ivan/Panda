# app/vision/estimador.py
"""Estimadores de nutrientes. El real usa SigLIP2 + CalorieK; el falso permite correr la CI sin torch ni pesos."""

from dataclasses import dataclass
from typing import Protocol

from PIL import Image

from . import NUTRIENTES


class EstimadorVision(Protocol):
    nombre: str
    version: str

    def predecir(self, imagen: Image.Image) -> dict[str, float]:
        """Recibe la imagen ya validada y sin metadatos. Devuelve kcal y gramos por nutriente."""
        ...


@dataclass
class EstimadorFalso:
    """Respuestas fijas y deterministas (CI y desarrollo sin GPU)."""

    valores: tuple[float, ...] = (450.0, 300.0, 15.0, 50.0, 25.0)
    nombre: str = "falso"
    version: str = "falso-1"

    def predecir(self, imagen: Image.Image) -> dict[str, float]:
        return dict(zip(NUTRIENTES, self.valores, strict=True))


class EstimadorSiglip:
    """Modelo entrenado en comida.ipynb (Opción A: CalorieK afinado con Nutrition5k)."""

    nombre = "siglip2-caloriek-n5k"

    def __init__(self, modelo, img_size: int, dispositivo, sha256: str):
        self.modelo, self.img_size, self.dispositivo = modelo, img_size, dispositivo
        self.version = sha256[:12]

    @classmethod
    def desde_checkpoint(cls, ruta, dispositivo: str, sha256: str) -> "EstimadorSiglip":
        import torch

        from .modelo import cargar_checkpoint

        if dispositivo == "auto":
            dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
        dev = torch.device(dispositivo)
        modelo, img_size = cargar_checkpoint(ruta, dev)
        return cls(modelo, img_size, dev, sha256)

    def predecir(self, imagen: Image.Image) -> dict[str, float]:
        import torch

        from .preprocesamiento import a_tensor

        x = a_tensor(imagen, self.img_size).to(self.dispositivo)
        with torch.inference_mode():
            y = self.modelo(x)[0].tolist()
        return dict(zip(NUTRIENTES, y, strict=True))
