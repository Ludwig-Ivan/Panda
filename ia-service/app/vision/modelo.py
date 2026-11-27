# app/vision/modelo.py
"""Port de `NutritionHead` y `NutritionModel` (comida.ipynb, sección 6) para inferencia (T-211).

Diferencias con el notebook, ambas a propósito:
- El backbone siempre se construye desde `vision_config` del checkpoint: el servicio nunca descarga SigLIP2
  de Hugging Face al arrancar (HF_HUB_OFFLINE=1 en la imagen).
- No incluye `load_caloriek` ni nada del entrenamiento.
Los nombres de capas y buffers son los mismos, así que `best.pt` carga sin renombrar llaves.
"""

from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F  # noqa: N812
from torch import nn
from transformers import SiglipVisionConfig, SiglipVisionModel


class NutritionHead(nn.Module):
    """Igual a la cabeza de CalorieK."""

    def __init__(self, d: int = 768):
        super().__init__()
        self.net = nn.Sequential(
            nn.LayerNorm(d),
            nn.Linear(d, 768),
            nn.GELU(),
            nn.Dropout(0.15),
            nn.Linear(768, 256),
            nn.GELU(),
            nn.Dropout(0.10),
            nn.Linear(256, 5),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.softplus(self.net(x))


class NutritionModel(nn.Module):
    """SigLIP2 + cabeza de regresión. Salida en kcal y gramos, en el orden de `app.vision.NUTRIENTES`."""

    def __init__(self, vision_config: dict[str, Any]):
        super().__init__()
        self.backbone = SiglipVisionModel(SiglipVisionConfig(**vision_config))
        self.head = NutritionHead(self.backbone.config.hidden_size)
        self.register_buffer("scale", torch.ones(5))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.backbone(pixel_values=x)
        f = out.pooler_output if out.pooler_output is not None else out.last_hidden_state[:, 0]
        return self.head(f.float()) * self.scale


_PREFIJO_V4 = "backbone.vision_model."  # transformers 4.x: SiglipVisionModel.vision_model.*
_PREFIJO_V5 = "backbone."  # transformers 5.x: el submódulo vision_model desaparece


class ErrorCheckpoint(RuntimeError):
    """El checkpoint no corresponde a la arquitectura esperada."""


def alinear_llaves(state: dict[str, torch.Tensor], esperadas: set[str]) -> dict[str, torch.Tensor]:
    """Adapta las llaves del backbone entre transformers 4.x y 5.x.

    `best.pt` se guarda con la versión de transformers que tenía Colab al entrenar; el servicio puede correr con otra.
    La arquitectura es la misma; solo cambia el prefijo de las llaves del backbone.
    """
    if set(state) == esperadas:
        return state

    def _v4_a_v5(k: str) -> str:
        return _PREFIJO_V5 + k[len(_PREFIJO_V4) :] if k.startswith(_PREFIJO_V4) else k

    def _v5_a_v4(k: str) -> str:
        if k.startswith(_PREFIJO_V5) and not k.startswith(_PREFIJO_V4):
            return _PREFIJO_V4 + k[len(_PREFIJO_V5) :]
        return k

    for convertir in (_v4_a_v5, _v5_a_v4):
        candidato = {convertir(k): v for k, v in state.items()}
        if set(candidato) == esperadas:
            return candidato
    faltan, sobran = sorted(esperadas - set(state))[:3], sorted(set(state) - esperadas)[:3]
    raise ErrorCheckpoint(f"Las llaves del checkpoint no coinciden con el modelo (faltan {faltan}, sobran {sobran})")


def cargar_checkpoint(ruta: Path, dispositivo: torch.device) -> tuple[NutritionModel, int]:
    """Carga `best.pt` con el formato que guarda el notebook: {"model": state_dict, "config": {...}}.

    Se intenta primero `weights_only=True`. El notebook usa `weights_only=False`; solo se recurre a eso si el archivo
    lo exige, y nunca antes de que `pesos.asegurar_pesos` haya verificado su SHA-256.
    """
    try:
        ckpt = torch.load(ruta, map_location=dispositivo, weights_only=True)
    except Exception:  # noqa: BLE001  pickle con objetos no permitidos; el SHA ya se verificó
        ckpt = torch.load(ruta, map_location=dispositivo, weights_only=False)  # noqa: S614
    config = ckpt["config"]
    vision_config = {k: v for k, v in config["vision_config"].items() if k != "transformers_version"}
    modelo = NutritionModel(vision_config)
    modelo.load_state_dict(alinear_llaves(ckpt["model"], set(modelo.state_dict())))
    modelo.to(dispositivo).eval()
    return modelo, int(config["img_size"])
