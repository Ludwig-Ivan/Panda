from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from panda.comun.errores import SinComidaDetectada, manejar_excepcion


def _contexto(request_id="abc123"):
    request = APIRequestFactory().get("/x")
    request.request_id = request_id
    return {"request": request}


def test_error_de_negocio_con_formato_de_la_api():
    r = manejar_excepcion(SinComidaDetectada(), _contexto())
    assert r.status_code == 422
    assert r.data == {
        "error": {
            "code": "NO_FOOD_DETECTED",
            "message": SinComidaDetectada.mensaje,
            "details": [],
            "requestId": "abc123",
        }
    }


def test_validacion_se_aplana_en_camel_case():
    exc = ValidationError({"peso_kg": ["Muy bajo."], "items": [{"porcion_g": ["Requerido."]}]})
    r = manejar_excepcion(exc, _contexto())
    assert r.status_code == 400
    assert [d["field"] for d in r.data["error"]["details"]] == ["pesoKg", "items[0].porcionG"]


def test_error_no_controlado_no_expone_detalles():
    r = manejar_excepcion(RuntimeError("password=secreto"), _contexto())
    assert r.status_code == 500 and r.data["error"]["code"] == "INTERNAL_ERROR"
    assert "secreto" not in str(r.data)
