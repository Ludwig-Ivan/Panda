# tests/test_actividad.py
"""T-223: caso de referencia, caso de 51 min, límites y cambio de compendio a los 60 años."""

import pytest

from app.actividad import calculo
from app.actividad.compendio import cargar
from app.config import RAIZ

CAMINAR_MODERADO = "1719060"  # adultos 3.8 MET · 60+ 5.3 MET
TV_SENTADO = "0702060"  # adultos 1.0 MET: sin gasto extra en modo neto


# --- Fórmula (funciones puras) -----------------------------------------------------------


def test_caso_de_referencia_del_srs():
    # El Apéndice A del SRS no trae el ejemplo desarrollado; se usa el caso de referencia del backend y de la API
    # Specification (70 kg, MET 6.8, neto): 7.105 kcal/min.
    assert round(calculo.kcal_por_minuto(6.8, 70, edad=30), 3) == 7.105


def test_caso_de_51_minutos():
    # Criterio de HU-85: 200 kg, MET 3.8, 500 kcal → 51 min (es el mismo resultado que muestra el notebook)
    assert calculo.minutos(500, 3.8, 200, edad=30) == 51


def test_modo_bruto():
    assert round(calculo.kcal_por_minuto(3.8, 200, edad=30, neto=False), 2) == 13.3
    assert calculo.minutos(500, 3.8, 200, edad=30, neto=False) == 38


@pytest.mark.parametrize(("edad", "k"), [(18, 3.5), (59, 3.5), (60, 2.7), (85, 2.7)])
def test_factor_de_oxigeno_cambia_a_los_60(edad, k):
    assert calculo.factor_o2(edad) == k


def test_neto_rechaza_met_sin_gasto_extra():
    with pytest.raises(ValueError):
        calculo.kcal_por_minuto(1.0, 70, edad=30)


def test_redondeo_half_up():
    assert calculo.redondear(50.5) == 51 and calculo.redondear(50.49) == 50


def test_compendios_exportados_del_notebook():
    comp = cargar(RAIZ / "data")
    assert len(comp.adultos.actividades) == len(comp.mayores.actividades) == 99
    assert comp.adultos.actividades[CAMINAR_MODERADO].met == 3.8
    assert comp.mayores.actividades[CAMINAR_MODERADO].met == 5.3
    assert comp.para_edad(59) is comp.adultos and comp.para_edad(60) is comp.mayores


# --- API -------------------------------------------------------------------------------------


def _calcular(cliente, auth, **datos):
    cuerpo = {"kcal": 500, "peso_kg": 200, "edad": 30, "codigo": CAMINAR_MODERADO} | datos
    return cliente.post("/v1/actividad/calcular", json=cuerpo, headers=auth)


def test_calcular_caso_de_51_minutos(cliente, auth):
    r = _calcular(cliente, auth)
    assert r.status_code == 200, r.text
    d = r.json()
    assert (d["minutos"], d["kcal_por_min"], d["tiempo"]) == (51, 9.8, "51 min")
    assert d["compendio"].startswith("Compendio de Actividad Física para Adultos")


def test_a_los_60_usa_el_compendio_de_adultos_mayores(cliente, auth):
    d59 = _calcular(cliente, auth, edad=59, peso_kg=70, kcal=300).json()
    d60 = _calcular(cliente, auth, edad=60, peso_kg=70, kcal=300).json()
    assert d59["met"] == 3.8 and d60["met"] == 5.3
    assert d60["compendio"] == "Compendio para Adultos Mayores 2024"
    assert d60["minutos"] == calculo.minutos(300, 5.3, 70, edad=60)  # (5.3−1)×2.7×70/200


@pytest.mark.parametrize(
    "cambio", [{"peso_kg": 29}, {"peso_kg": 301}, {"edad": 17}, {"edad": 101}, {"kcal": 0}, {"kcal": 5001}]
)
def test_limites_de_entrada(cliente, auth, cambio):
    r = _calcular(cliente, auth, **cambio)
    assert r.status_code == 422 and r.json()["error"]["code"] == "VALIDATION_ERROR"


def test_codigo_inexistente_responde_404(cliente, auth):
    assert _calcular(cliente, auth, codigo="9999999").status_code == 404


def test_neto_con_actividad_sin_gasto_extra_responde_422(cliente, auth):
    assert _calcular(cliente, auth, codigo=TV_SENTADO).status_code == 422


def test_mas_de_90_minutos_sugiere_repartir_sin_pedir_comer_menos(cliente, auth):
    d = _calcular(cliente, auth, peso_kg=60, kcal=900).json()
    assert d["minutos"] > 90 and d["supera_limite_continuo"]
    assert any("repartir" in a for a in d["avisos"])
    texto = " ".join(d["avisos"]).lower()
    prohibidas = ("comer menos", "come menos", "reduce", "evita comer", "dieta")  # RN-01 a RN-03
    assert not any(p in texto for p in prohibidas)


def test_actividad_vigorosa_trae_aviso(cliente, auth):
    d = _calcular(cliente, auth, codigo="1207060").json()  # correr 11.3 km/h: 11 MET
    assert any("vigorosa" in a for a in d["avisos"])


def test_catalogo_ordenado_y_sin_reposo_en_modo_neto(cliente, auth):
    d = cliente.get("/v1/actividad/catalogo?edad=30", headers=auth).json()
    mets = [a["met"] for a in d["actividades"]]
    assert mets == sorted(mets) and min(mets) > 1.0 and len(mets) == 95
    caminar = cliente.get("/v1/actividad/catalogo?edad=30&categoria=Caminar", headers=auth).json()["actividades"]
    assert caminar and {a["categoria"] for a in caminar} == {"Caminar"}


def test_catalogo_de_adultos_mayores(cliente, auth):
    d = cliente.get("/v1/actividad/catalogo?edad=65", headers=auth).json()
    assert d["factor_o2"] == 2.7 and not any(a["estimado"] for a in d["actividades"])
