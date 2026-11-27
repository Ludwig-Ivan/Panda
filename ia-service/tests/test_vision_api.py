# tests/test_vision_api.py
"""Criterios de HU-83 con el EstimadorFalso: contrato, 415, 413, 422, EXIF y rango ±%MAE."""

import io

import pytest
from PIL import Image

from app.config import RAIZ
from app.errores import FormatoNoSoportado, ImagenMuyPequena
from app.vision.imagen import validar_y_limpiar
from app.vision.rango import AVISOS, Metricas, rango

from .conftest import imagen_bytes

MB = 1024 * 1024


def _estimar(cliente, auth, datos, nombre="foto.jpg", tipo="image/jpeg"):
    return cliente.post("/v1/vision/estimar", files={"foto": (nombre, datos, tipo)}, headers=auth)


def test_contrato_de_respuesta(cliente, auth):
    r = _estimar(cliente, auth, imagen_bytes())
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["modelo"] == {"nombre": "falso", "version": "falso-1"}
    assert set(d["nutrientes"]) == {"calorias", "masa", "grasa", "carbohidrato", "proteina"}
    kcal = d["nutrientes"]["calorias"]
    # %MAE real del test de Nutrition5k para calorías: 17.4 %
    assert kcal == {"valor": 450.0, "min": 371.7, "max": 528.3, "unidad": "kcal", "pct_mae": 17.4}
    assert d["nutrientes"]["proteina"]["unidad"] == "g"
    assert d["avisos"] == list(AVISOS) and isinstance(d["latencia_ms"], int)


@pytest.mark.parametrize("formato", ["JPEG", "PNG", "WEBP"])
def test_acepta_jpeg_png_y_webp(cliente, auth, formato):
    assert _estimar(cliente, auth, imagen_bytes(formato=formato)).status_code == 200


def test_rechaza_formato_no_soportado_por_contenido(cliente, auth):
    r = _estimar(cliente, auth, b"esto no es una imagen", nombre="trampa.jpg")  # extensión .jpg, contenido texto
    assert r.status_code == 415 and r.json()["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"
    buffer = io.BytesIO()
    Image.new("RGB", (800, 600)).save(buffer, "GIF")
    assert _estimar(cliente, auth, buffer.getvalue(), nombre="a.gif", tipo="image/gif").status_code == 415


def test_rechaza_mas_de_10_mb(cliente, auth):
    r = _estimar(cliente, auth, b"\x89PNG" + b"0" * (10 * MB))
    assert r.status_code == 413


def test_rechaza_resolucion_insuficiente(cliente, auth):
    r = _estimar(cliente, auth, imagen_bytes(300, 200))
    assert r.status_code == 422 and r.json()["error"]["code"] == "IMAGE_TOO_SMALL"
    assert _estimar(cliente, auth, imagen_bytes(640, 480)).status_code == 200  # el mínimo exacto sí pasa
    assert _estimar(cliente, auth, imagen_bytes(480, 640)).status_code == 200  # vertical también


def test_falta_el_campo_foto(cliente, auth):
    r = cliente.post("/v1/vision/estimar", headers=auth)
    assert r.status_code == 422 and r.json()["error"]["details"][0]["field"] == "foto"


def _exif_con_orientacion_y_gps() -> bytes:
    exif = Image.Exif()
    exif[0x0112] = 6  # Orientation: girar 90°
    exif[0x010F] = "Fabricante"  # Make
    exif[0x8825] = {1: "N", 2: (19.0, 25.0, 0.0)}  # GPSInfo
    return exif.tobytes()


def test_elimina_el_exif_y_respeta_la_orientacion():
    datos = imagen_bytes(800, 600, exif=_exif_con_orientacion_y_gps())
    assert Image.open(io.BytesIO(datos)).getexif()  # la original sí trae EXIF
    limpia = validar_y_limpiar(datos, 10 * MB, 640, 480)
    assert limpia.size == (600, 800)  # rotada según Orientation
    assert not limpia.getexif() and "exif" not in limpia.info and limpia.mode == "RGB"


def test_validacion_directa():
    with pytest.raises(FormatoNoSoportado):
        validar_y_limpiar(b"\x00" * 100, 10 * MB, 640, 480)
    with pytest.raises(ImagenMuyPequena):
        validar_y_limpiar(imagen_bytes(639, 480), 10 * MB, 640, 480)


def test_el_rango_usa_el_pct_mae_del_test_oficial():
    m = Metricas.desde_archivo(RAIZ / "modelo" / "test_metrics.json")
    assert round(m.pct_mae["calorias"], 1) == 17.4 and round(m.mean_pct_mae, 1) == 21.2
    bajo, alto = rango(100, 25)
    assert (bajo, alto) == (75, 125)
    assert rango(10, 150) == (0.0, 25.0)  # nunca negativo


def test_metricas_con_claves_en_ingles_se_rechazan(tmp_path):
    # Es el bug de T-208: el notebook leía "calories" donde el CSV y el JSON usan "calorias"
    p = tmp_path / "m.json"
    p.write_text('{"calories": {"mae": 1, "pct_mae": 1}, "mean_pct_mae": 1}')
    with pytest.raises(ValueError, match="calorias"):
        Metricas.desde_archivo(p)
