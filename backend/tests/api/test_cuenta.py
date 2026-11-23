import pytest
from django.conf import settings

from panda.catalogos.models import Actividad

pytestmark = pytest.mark.django_db
PERFIL = {"edad": 29, "sexo": "femenino", "pesoKg": 62.5, "estaturaCm": 163, "nivelActividad": "ligero"}


def test_perfil_se_crea_y_actualiza(api, crear_usuario):
    api.force_authenticate(crear_usuario(completo=False))
    assert api.get("/api/v1/perfil").status_code == 404
    r = api.put("/api/v1/perfil", PERFIL, format="json")
    assert r.status_code == 200 and r.json()["pesoKg"] == 62.5
    assert api.get("/api/v1/usuarios/me").json()["perfilCompleto"] is True


def test_perfil_fuera_de_rango(cliente):
    r = cliente.put("/api/v1/perfil", {**PERFIL, "edad": 15}, format="json")
    assert r.status_code == 400 and r.json()["error"]["details"][0]["field"] == "edad"


def test_solo_se_acepta_la_version_vigente_de_los_avisos(api, crear_usuario):
    api.force_authenticate(crear_usuario(completo=False))
    viejo = {"consentimientos": [{"tipo": "privacidad", "version": "2020-01"}]}
    assert api.post("/api/v1/consentimientos", viejo, format="json").status_code == 400
    vigentes = [{"tipo": t, "version": v} for t, v in settings.PANDA["CONSENTIMIENTOS_VIGENTES"].items()]
    assert api.post("/api/v1/consentimientos", {"consentimientos": vigentes}, format="json").json()["pendientes"] == []


def test_preferencias_sin_duplicados_y_validadas(cliente, catalogo):
    ids = list(Actividad.objects.values_list("id", flat=True)[:2])
    r = cliente.put("/api/v1/perfil/preferencias-actividad", {"actividadIds": ids + ids}, format="json")
    assert r.json()["actividadIds"] == ids
    r = cliente.put("/api/v1/perfil/preferencias-actividad", {"actividadIds": [999999]}, format="json")
    assert r.status_code == 404


def test_desactivar_el_guardado_de_fotos(cliente):
    r = cliente.patch("/api/v1/usuarios/me", {"guardarFotos": False}, format="json")
    assert r.status_code == 200 and r.json()["guardarFotos"] is False
