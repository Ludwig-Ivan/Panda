import pytest
from hypothesis import given
from hypothesis import strategies as st

from panda.dominio.calorias import EntradaItem, FuenteKcal, ResultadoItem, calcular_item, redondear, totalizar


def test_ejemplo_de_la_api():
    tacos = calcular_item(EntradaItem(180, 175.56, 0.84, FuenteKcal.CATALOGO, False))
    frijoles = calcular_item(EntradaItem(150, 89, 0.46, FuenteKcal.CATALOGO, False))
    assert (tacos.kcal, tacos.kcal_min, tacos.kcal_max, tacos.requiere_revision) == (316, 253, 379, False)
    assert (frijoles.kcal, frijoles.kcal_min, frijoles.kcal_max, frijoles.requiere_revision) == (134, 92, 176, True)
    total = totalizar([tacos, frijoles])
    assert (total.total, total.min, total.max) == (450, 350, 560)


def test_usuario_usa_factor_fijo():
    r = calcular_item(EntradaItem(100, 100, None, FuenteKcal.USUARIO, True))
    assert (r.kcal_min, r.kcal_max) == (90, 110)


def test_estimado_ia_amplia_el_rango_y_pide_revision():
    r = calcular_item(EntradaItem(100, 100, 1.0, FuenteKcal.ESTIMADO_IA, False))
    assert (r.kcal_min, r.kcal_max, r.requiere_revision) == (70, 130, True)


def test_redondeo_half_up():
    assert redondear(133.5) == 134 and redondear(445, 10) == 450


@pytest.mark.parametrize("gramos,kcal", [(0, 100), (-1, 100), (100, -5)])
def test_entradas_invalidas(gramos, kcal):
    with pytest.raises(ValueError):
        calcular_item(EntradaItem(gramos, kcal, 0.5, FuenteKcal.CATALOGO, False))


@given(
    gramos=st.floats(1, 2000),
    kcal_100g=st.floats(0, 900),
    confianza=st.floats(0, 1),
    fuente=st.sampled_from(list(FuenteKcal)),
    usuario=st.booleans(),
)
def test_el_rango_siempre_contiene_el_valor(gramos, kcal_100g, confianza, fuente, usuario):
    r = calcular_item(EntradaItem(gramos, kcal_100g, confianza, fuente, usuario))
    assert 0 <= r.kcal_min <= r.kcal <= r.kcal_max


@given(st.lists(st.tuples(st.integers(0, 2000), st.floats(0, 0.6)), max_size=20))
def test_total_dentro_del_rango(valores):
    items = [ResultadoItem(k, redondear(k * (1 - f)), redondear(k * (1 + f))) for k, f in valores]
    t = totalizar(items)
    assert t.min <= t.total <= t.max and t.total % 10 == 0