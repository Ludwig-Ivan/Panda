import pytest
from django.conf import settings

pytestmark = pytest.mark.django_db
COOKIE = settings.AUTH_COOKIE["NOMBRE"]


def _registro(api):
    datos = {
        "email": "nuevo@ejemplo.com",
        "password": "Panda2026segura",
        "mayorEdad": True,
        "consentimientos": [{"tipo": t, "version": v} for t, v in settings.PANDA["CONSENTIMIENTOS_VIGENTES"].items()],
    }
    return api.post("/api/v1/auth/registro", datos, format="json")


def test_logout_revoca_el_refresh(api):
    r = _registro(api)
    refresh = api.cookies[COOKIE].value
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {r.json()['accessToken']}")
    assert api.post("/api/v1/auth/logout").status_code == 204
    api.cookies[COOKIE] = refresh
    assert api.post("/api/v1/auth/refresh").status_code == 401


def test_login_limitado_a_10_intentos_cada_15_min(api, usuario):
    for _ in range(10):
        api.post("/api/v1/auth/login", {"email": usuario.email, "password": "mala1234"}, format="json")
    r = api.post("/api/v1/auth/login", {"email": usuario.email, "password": "mala1234"}, format="json")
    assert r.status_code == 429 and r.json()["error"]["code"] == "RATE_LIMITED" and r["Retry-After"]
