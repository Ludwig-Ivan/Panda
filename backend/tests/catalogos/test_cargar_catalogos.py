import pytest
from django.core.management import call_command

from panda.catalogos.models import Actividad, Alimento

pytestmark = pytest.mark.django_db
CABECERA = "nombre,alias,kcal_100g,porcion_tipica_g,fuente_ref\n"


def test_carga_idempotente_y_el_curado_gana(tmp_path):
    (tmp_path / "alimentos_fdc.csv").write_text(CABECERA + "Arroz rojo,,130,100,1\n", encoding="utf-8")
    (tmp_path / "alimentos_curados.csv").write_text(
        CABECERA + "Arroz rojo,arroz,150,120,curado-004\n", encoding="utf-8"
    )
    (tmp_path / "actividades_met.csv").write_text(
        "codigo_compendium,nombre,met,intensidad\n12020,Trotar,7.0,vigorosa\n", encoding="utf-8"
    )
    call_command("cargar_catalogos", dir=str(tmp_path))
    call_command("cargar_catalogos", dir=str(tmp_path))  # la segunda vez no duplica
    arroz = Alimento.objects.get()
    assert (arroz.fuente, float(arroz.kcal_100g), arroz.alias) == ("curado", 150.0, ["arroz"])
    assert Actividad.objects.count() == 1


def test_los_csv_del_repositorio_cumplen_las_restricciones():
    call_command("cargar_catalogos")  # falla con IntegrityError si un MET no cuadra con su intensidad
    assert Alimento.objects.count() >= 50, "T-138: el catálogo debe tener al menos 50 alimentos"
    assert Actividad.objects.filter(intensidad="ligera").exists()