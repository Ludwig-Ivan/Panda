import pytest
from django.conf import settings

pytestmark = pytest.mark.django_db
COOKIE = settings.AUTH_COOKIE["NOMBRE"]


def _registro(api, **extra):
    datos = {
        "email": "Nuevo@Ejemplo.com",
        "password": "Panda2026segura",
        "mayorEdad": True,
        "consentimientos": [{"tipo": t, "version": v} for t, v in settings.PANDA["CONSENTIMIENTOS_VIGENTES"].items()],
        **extra,
    }
    return api.post("/api/v1/auth/registro", datos, format="json")


def test_registro_crea_sesion_y_cookie(api):
    r = _registro(api)
    assert r.status_code == 201
    assert r.json()["usuario"]["email"] == "nuevo@ejemplo.com"
    assert r.cookies[COOKIE]["httponly"] and r.cookies[COOKIE]["path"] == "/api/v1/auth"


def test_registro_menor_de_edad(api):
    assert _registro(api, mayorEdad=False).json()["error"]["code"] == "AGE_REQUIREMENT"


def test_registro_sin_consentimiento_vigente(api):
    r = _registro(api, consentimientos=[{"tipo": "privacidad", "version": "2020-01"}])
    assert r.status_code == 422 and r.json()["error"]["code"] == "CONSENT_REQUIRED"


def test_login_incorrecto_es_generico(api, usuario):
    r = api.post("/api/v1/auth/login", {"email": usuario.email, "password": "otra1234"}, format="json")
    assert r.status_code == 401 and r.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_refresh_rota_y_detecta_reutilizacion(api):
    _registro(api)
    viejo = api.cookies[COOKIE].value
    r1 = api.post("/api/v1/auth/refresh")
    assert r1.status_code == 200
    nuevo = api.cookies[COOKIE].value
    assert nuevo != viejo

    api.cookies[COOKIE] = viejo  # alguien reutiliza el token rotado
    assert api.post("/api/v1/auth/refresh").status_code == 401
    api.cookies[COOKIE] = nuevo  # y eso revocó también la sesión legítima
    assert api.post("/api/v1/auth/refresh").status_code == 401
