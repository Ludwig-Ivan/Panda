import csv
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from panda.catalogos.models import Actividad, Alimento, FuenteAlimento
from panda.dominio.texto import normalizar


class Command(BaseCommand):
    help = "Carga o actualiza los catálogos desde data/*.csv. Se puede ejecutar varias veces."

    def add_arguments(self, parser):
        parser.add_argument("--dir", default=str(settings.BASE_DIR / "data"))

    @transaction.atomic
    def handle(self, *args, **opciones):
        base = Path(opciones["dir"])
        # FDC primero y curados después: si un nombre se repite, gana el curado
        n_alimentos = self._alimentos(base / "alimentos_fdc.csv", FuenteAlimento.FDC)
        n_alimentos += self._alimentos(base / "alimentos_curados.csv", FuenteAlimento.CURADO)
        n_actividades = self._actividades(base / "actividades_met.csv")
        self.stdout.write(self.style.SUCCESS(f"Alimentos:{n_alimentos} · Actividades:{n_actividades}"))

    def _filas(self, ruta: Path):
        if not ruta.exists():
            self.stdout.write(self.style.WARNING(f"No existe{ruta.name}; se omite"))
            return []
        with ruta.open(encoding="utf-8") as archivo:
            return [f for f in csv.DictReader(archivo) if not f[next(iter(f))].startswith("#")]

    def _alimentos(self, ruta: Path, fuente: str) -> int:
        filas = self._filas(ruta)
        for fila in filas:
            Alimento.objects.update_or_create(
                nombre_normalizado=normalizar(fila["nombre"]),
                defaults={
                    "nombre": fila["nombre"].strip(),
                    "alias": [a for a in fila.get("alias", "").split("|") if a.strip()],
                    "kcal_100g": Decimal(fila["kcal_100g"]),
                    "porcion_tipica_g": Decimal(fila["porcion_tipica_g"]) if fila.get("porcion_tipica_g") else None,
                    "fuente": fuente,
                    "fuente_ref": fila.get("fuente_ref") or None,
                    "activo": True,
                },
            )
        return len(filas)

    def _actividades(self, ruta: Path) -> int:
        filas = self._filas(ruta)
        for fila in filas:
            Actividad.objects.update_or_create(
                codigo_compendium=fila["codigo_compendium"].strip(),
                defaults={
                    "nombre": fila["nombre"].strip(),
                    "met": Decimal(fila["met"]),
                    "intensidad": fila["intensidad"].strip(),
                    "activo": True,
                },
            )
        return len(filas)