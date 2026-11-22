# tests/dominio/test_recomendacion.py
from hypothesis import given
from hypothesis import strategies as st

from panda.dominio.recomendacion import (
    ActividadCatalogo,
    Intensidad,
    NivelActividad,
    ParametrosRecomendacion,
    kcal_por_minuto,
    planificar,
    recomendar,
)

CAMINAR = ActividadCatalogo(1, "Caminar a paso moderado", 3.5, Intensidad.MODERADA)
BICI = ActividadCatalogo(4, "Bicicleta recreativa", 6.8, Intensidad.VIGOROSA)
TROTAR = ActividadCatalogo(5, "Trotar", 7.0, Intensidad.VIGOROSA)
YOGA = ActividadCatalogo(6, "Yoga", 2.5, Intensidad.LIGERA)
CATALOGO = [CAMINAR, BICI, TROTAR, YOGA]


def test_formula_met_neto():
    assert round(kcal_por_minuto(6.8, 70), 3) == 7.105


def test_ejemplo_450_kcal_70_kg_moderado():
    r = recomendar(450, 70, NivelActividad.MODERADO, CATALOGO, preferidas=set())
    resumen = {a.actividad.nombre: (a.duracion_min, a.sesiones, a.kcal_estimadas) for a in r.actividades}
    assert resumen["Bicicleta recreativa"] == (65, 1, 462)
    assert resumen["Trotar"] == (65, 1, 478)
    assert resumen["Caminar a paso moderado"] == (160, 4, 490)
    assert r.formula_version == "met-neto-v1"


def test_sedentario_no_recibe_vigorosas():
    r = recomendar(450, 70, NivelActividad.SEDENTARIO, CATALOGO, set())
    assert all(a.actividad.intensidad != Intensidad.VIGOROSA for a in r.actividades)


def test_preferidas_van_primero():
    r = recomendar(300, 70, NivelActividad.ALTO, CATALOGO, preferidas={5})
    assert r.actividades[0].actividad.id == 5 and r.actividades[0].es_preferida


def test_descarta_si_supera_180_min():
    assert planificar(2000, 2.0, ParametrosRecomendacion()) is None


def test_cero_kcal_devuelve_lista_vacia_con_mensaje():
    r = recomendar(0, 70, NivelActividad.MODERADO, CATALOGO, set())
    assert r.actividades == () and r.mensaje


@given(kcal=st.integers(1, 5000), peso=st.floats(30, 300), nivel=st.sampled_from(list(NivelActividad)))
def test_limites_de_seguridad(kcal, peso, nivel):
    r = recomendar(kcal, peso, nivel, CATALOGO, set())
    for a in r.actividades:
        assert a.duracion_min % 5 == 0 and 5 <= a.duracion_min <= 180
        assert 1 <= a.sesiones <= 4
        assert a.duracion_min // a.sesiones <= 90
        assert a.kcal_estimadas >= kcal - 1  # la duración se redondea hacia arriba
