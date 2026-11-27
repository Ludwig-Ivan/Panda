# app/vision/rango.py
"""Rango de cada nutriente con el %MAE del test oficial de Nutrition5k (T-213).

min = valor × (1 − %MAE/100) y max = valor × (1 + %MAE/100). El %MAE sale de `modelo/test_metrics.json`,
que se publica junto con `best.pt`: si se reentrena el modelo, el rango se actualiza solo.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from . import NUTRIENTES

AVISOS = (
    "Las calorías y los nutrientes son una estimación aproximada a partir de la foto.",
    "Panda no sustituye la orientación de un profesional de la salud o la nutrición.",
)


@dataclass(frozen=True)
class Metricas:
    pct_mae: dict[str, float]
    mean_pct_mae: float

    @classmethod
    def desde_archivo(cls, ruta: Path) -> "Metricas":
        datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
        faltan = [n for n in NUTRIENTES if n not in datos]
        if faltan:
            # Es justo el error que corrige T-208: claves en inglés (calories) en lugar de español (calorias)
            raise ValueError(f"test_metrics.json no tiene las claves {faltan}")
        return cls({n: float(datos[n]["pct_mae"]) for n in NUTRIENTES}, float(datos["mean_pct_mae"]))


def rango(valor: float, pct_mae: float) -> tuple[float, float]:
    factor = pct_mae / 100
    return max(0.0, valor * (1 - factor)), valor * (1 + factor)
