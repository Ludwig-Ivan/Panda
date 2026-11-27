# tests/regresion/test_regresion_fotos.py
"""T-214: regresión con 10 fotos fijas contra los valores del notebook, y medición de latencia.

Necesita los pesos reales, así que NO corre en la CI. Para correrla:

    export IA_MODELO_PATH=/ruta/a/best.pt
    pytest -m regresion -s

Preparación (una sola vez): pon 10 fotos en tests/regresion/fotos/ y genera `esperado.json` con la celda que viene
en tests/regresion/fotos/README.md, ejecutada en el notebook con el mismo best.pt.
Criterio de HU-83: cada nutriente queda a ±1 % de lo que da el notebook.
"""

import hashlib
import json
import os
import statistics
import time
from pathlib import Path

import pytest
from PIL import Image

pytestmark = pytest.mark.regresion

FOTOS = Path(__file__).parent / "fotos"
ESPERADO = FOTOS / "esperado.json"
PESOS = os.getenv("IA_MODELO_PATH")


@pytest.fixture(scope="module")
def estimador():
    if not PESOS or not Path(PESOS).exists():
        pytest.skip("Define IA_MODELO_PATH con la ruta a best.pt para correr la regresión")
    if not ESPERADO.exists():
        pytest.skip("Falta tests/regresion/fotos/esperado.json (ver README de esa carpeta)")
    from app.vision.estimador import EstimadorSiglip

    sha = hashlib.sha256(Path(PESOS).read_bytes()).hexdigest()
    return EstimadorSiglip.desde_checkpoint(PESOS, os.getenv("IA_DISPOSITIVO", "auto"), sha)


def test_diez_fotos_igual_que_el_notebook(estimador):
    esperado = json.loads(ESPERADO.read_text(encoding="utf-8"))
    assert len(esperado) >= 10, "La regresión pide 10 fotos fijas"
    latencias = []
    for nombre, valores in esperado.items():
        imagen = Image.open(FOTOS / nombre).convert("RGB")
        inicio = time.monotonic()
        obtenido = estimador.predecir(imagen)
        latencias.append((time.monotonic() - inicio) * 1000)
        for nutriente, valor in valores.items():
            assert obtenido[nutriente] == pytest.approx(valor, rel=0.01), f"{nombre} · {nutriente}"
    latencias.sort()
    p95 = latencias[max(0, round(0.95 * len(latencias)) - 1)]
    print(
        f"\nLatencia de inferencia: mediana {statistics.median(latencias):.0f} ms · p95 {p95:.0f} ms "
        f"· dispositivo {estimador.dispositivo}"
    )
