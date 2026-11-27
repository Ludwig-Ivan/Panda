"""Calcula el SHA-256 de los artefactos del modelo y escribe modelo/manifiesto.json (T-209).

Uso (desde ia-service/, con best.pt descargado de Drive: MyDrive/n5k_runs/caloriek_ft/):

    python scripts/publicar_modelo.py /ruta/a/best.pt modelo/test_metrics.json --version v1

Después publica los archivos como un release de GitHub (el asset admite hasta 2 GB) y configura el servicio:

    gh release create modelo-v1 /ruta/a/best.pt modelo/test_metrics.json modelo/FICHA_MODELO.md \
        modelo/manifiesto.json -R Ludwig-Ivan/Panda -t "Modelo de visión v1" -n "SigLIP2 + CalorieK (Nutrition5k)"

    IA_MODELO_URL=https://github.com/Ludwig-Ivan/Panda/releases/download/modelo-v1/best.pt
    IA_MODELO_SHA256=<sha256 de best.pt que imprime este script>
"""

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path


def sha256_de(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("pesos", type=Path)
    p.add_argument("metricas", type=Path)
    p.add_argument("--version", default="v1")
    p.add_argument("--salida", type=Path, default=Path("modelo/manifiesto.json"))
    args = p.parse_args()

    metricas = json.loads(args.metricas.read_text(encoding="utf-8"))
    manifiesto = {
        "nombre": "siglip2-caloriek-n5k",
        "version": args.version,
        "generado": datetime.now(UTC).isoformat(timespec="seconds"),
        "artefactos": {
            "best.pt": {"sha256": sha256_de(args.pesos), "bytes": args.pesos.stat().st_size},
            "test_metrics.json": {"sha256": sha256_de(args.metricas), "bytes": args.metricas.stat().st_size},
        },
        "metricas_test": {
            "mean_pct_mae": metricas["mean_pct_mae"],
            "pct_mae": {k: v["pct_mae"] for k, v in metricas.items() if isinstance(v, dict)},
        },
    }
    args.salida.write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifiesto["artefactos"], indent=2))
    print(f"\nIA_MODELO_SHA256={manifiesto['artefactos']['best.pt']['sha256']}")
    print("Copia ese valor en la tabla de artefactos de modelo/FICHA_MODELO.md.")


if __name__ == "__main__":
    main()
