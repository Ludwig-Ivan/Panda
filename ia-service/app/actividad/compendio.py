# app/actividad/compendio.py
"""Carga los compendios 2024 exportados del notebook (T-220) y elige el que corresponde a la edad (T-221)."""

import csv
from dataclasses import dataclass
from pathlib import Path

EDAD_ADULTO_MAYOR = 60
K_ADULTOS = 3.5  # mL O2/kg/min que vale 1 MET (Compendio de Adultos 2024)
K_MAYORES = 2.7  # Compendio de Adultos Mayores 2024 (MET60)


@dataclass(frozen=True)
class Actividad:
    codigo: str
    categoria: str
    actividad: str
    met: float
    estimado: bool  # el MET de adulto se estimó desde el MET60 porque no está en el compendio de adultos


@dataclass(frozen=True)
class Compendio:
    nombre: str
    factor_o2: float
    actividades: dict[str, Actividad]


@dataclass(frozen=True)
class Compendios:
    adultos: Compendio
    mayores: Compendio

    def para_edad(self, edad: int) -> Compendio:
        return self.mayores if edad >= EDAD_ADULTO_MAYOR else self.adultos


def _leer(ruta: Path, nombre: str, k: float) -> Compendio:
    with ruta.open(encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    actividades = {
        r["codigo"]: Actividad(r["codigo"], r["categoria"], r["actividad"], float(r["met"]), r.get("estimado") == "1")
        for r in filas
    }
    return Compendio(nombre, k, actividades)


def cargar(directorio: Path) -> Compendios:
    directorio = Path(directorio)
    adultos = _leer(
        directorio / "compendio_adultos_2024.csv", "Compendio de Actividad Física para Adultos 2024", K_ADULTOS
    )
    mayores = _leer(directorio / "compendio_adultos_mayores_2024.csv", "Compendio para Adultos Mayores 2024", K_MAYORES)
    return Compendios(adultos=adultos, mayores=mayores)
