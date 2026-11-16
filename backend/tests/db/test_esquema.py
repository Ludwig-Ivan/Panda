from decimal import Decimal

import pytest
from django.db import IntegrityError, connection

from panda.catalogos.models import Actividad, Alimento
from panda.identidad.models import Perfil, Usuario

pytestmark = pytest.mark.django_db
PASSWORD = "Panda2026segura"


def test_email_se_guarda_en_minusculas():
    u = Usuario.objects.create_user(email="Ana@Ejemplo.COM", password=PASSWORD, mayor_edad_declarado=True)
    assert u.email == "ana@ejemplo.com"


def test_bd_rechaza_menores_de_edad():
    with pytest.raises(IntegrityError):
        Usuario.objects.create_user(email="x@x.com", password=PASSWORD, mayor_edad_declarado=False)


def test_bd_rechaza_perfil_fuera_de_rango():
    u = Usuario.objects.create_user(email="y@x.com", password=PASSWORD, mayor_edad_declarado=True)
    with pytest.raises(IntegrityError):
        Perfil.objects.create(
            usuario=u,
            edad=15,
            sexo="femenino",
            peso_kg=Decimal("60"),
            estatura_cm=Decimal("160"),
            nivel_actividad="ligero",
        )


def test_intensidad_debe_ser_coherente_con_el_met():
    with pytest.raises(IntegrityError):
        Actividad.objects.create(codigo_compendium="x", nombre="X", met=Decimal("2.0"), intensidad="vigorosa")


def test_alimento_normaliza_nombre_y_alias():
    a = Alimento.objects.create(
        nombre="  Jamón SERRANO ", alias=["Jamón", "jamon"], kcal_100g=Decimal("240"), fuente="curado"
    )
    assert a.nombre_normalizado == "jamon serrano" and a.alias == ["jamon"]


@pytest.mark.parametrize(
    "constraint,accion",
    [
        ("fk_comida_items_alimento", "n"),  # SET NULL
        ("fk_comidas_usuario", "c"),  # CASCADE
        ("fk_recomendacion_items_actividad", "r"),  # RESTRICT
    ],
)
def test_on_delete_definido_en_la_bd(constraint, accion):
    with connection.cursor() as cursor:
        cursor.execute("SELECT confdeltype FROM pg_constraint WHERE conname =%s", [constraint])
        assert cursor.fetchone()[0] == accion


def test_health_responde_ok(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["checks"]["database"] == "ok"
    assert r["X-Request-Id"]
