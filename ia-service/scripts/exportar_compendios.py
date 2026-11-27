"""Exporta los compendios 2024 que trae comida.ipynb (sección 11, COMPENDIO_CSV) a dos CSV (T-220).

Uso: python scripts/exportar_compendios.py ../comida.ipynb data/

- data/compendio_adultos_2024.csv          MET del Compendio de Actividad Física para Adultos 2024 (19-59 años)
- data/compendio_adultos_mayores_2024.csv  MET del Compendio para Adultos Mayores 2024 (MET60, 60 años o más)

En ambos, `codigo` es el código del compendio de adultos mayores (el que usa el notebook como llave), para que una
misma actividad tenga el mismo identificador sin importar la edad. Las filas que no existen en el compendio de adultos
traen `estimado=1` (el notebook las estima a partir del MET60).
"""

import csv
import io
import json
import re
import sys
from pathlib import Path


def leer_compendio(notebook: Path) -> list[dict]:
    nb = json.loads(notebook.read_text(encoding="utf-8"))
    for celda in nb["cells"]:
        fuente = "".join(celda["source"])
        m = re.search(r'COMPENDIO_CSV = """\n(.*?)"""', fuente, re.S)
        if m:
            return list(csv.DictReader(io.StringIO(m.group(1))))
    raise SystemExit("No encontré COMPENDIO_CSV en el notebook")


def main(notebook: str, destino: str) -> None:
    filas = leer_compendio(Path(notebook))
    salida = Path(destino)
    salida.mkdir(parents=True, exist_ok=True)

    with (salida / "compendio_adultos_2024.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["codigo", "codigo_compendio", "categoria", "actividad", "met", "estimado", "actividad_original"])
        for r in filas:
            estimado = r["fuente_met_adulto"].startswith("estimado")
            w.writerow(
                [
                    r["codigo"],
                    r["codigo_adulto"],
                    r["categoria"],
                    r["actividad"],
                    r["met_adulto"],
                    int(estimado),
                    r["actividad_original"],
                ]
            )

    with (salida / "compendio_adultos_mayores_2024.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["codigo", "categoria", "actividad", "met", "actividad_original"])
        for r in filas:
            w.writerow([r["codigo"], r["categoria"], r["actividad"], r["met60"], r["actividad_original"]])

    print(f"{len(filas)} actividades exportadas a {salida}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
