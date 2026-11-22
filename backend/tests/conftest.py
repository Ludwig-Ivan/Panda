from decimal import Decimal
from io import BytesIO

import pytest
from django.conf import settings
from django.core.cache import cache, caches
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from panda.catalogos.models import Actividad, Alimento
from panda.estimacion.resiliencia import reiniciar_breaker
from panda.identidad.models import Consentimiento, Perfil, Usuario

PASSWORD = "Panda2026segura"


@pytest.fixture(autouse=True)
def _aislar_estado():
    cache.clear()
    caches["local"].clear()
    reiniciar_breaker()
    yield


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def crear_usuario(db):
    def _crear(email="ana@ejemplo.com", completo=True, nivel="moderado", peso="70"):
        usuario = Usuario.objects.create_user(email=email, password=PASSWORD, mayor_edad_declarado=True)
        if completo:
            Perfil.objects.create(
                usuario=usuario,
                edad=29,
                sexo="femenino",
                peso_kg=Decimal(peso),
                estatura_cm=Decimal("163"),
                nivel_actividad=nivel,
            )
            for tipo, version in settings.PANDA["CONSENTIMIENTOS_VIGENTES"].items():
                Consentimiento.objects.create(usuario=usuario, tipo=tipo, version=version)
        return usuario

    return _crear


@pytest.fixture
def usuario(crear_usuario):
    return crear_usuario()


@pytest.fixture
def cliente(api, usuario):
    api.force_authenticate(usuario)
    return api


@pytest.fixture
def catalogo(db):
    Alimento.objects.create(nombre="Tacos de pollo", kcal_100g=Decimal("175.56"), fuente="curado")
    Alimento.objects.create(
        nombre="Frijoles de la olla",
        alias=["frijoles"],
        kcal_100g=Decimal("89"),
        porcion_tipica_g=Decimal("150"),
        fuente="curado",
    )
    for codigo, nombre, met, intensidad in [
        ("17200", "Caminar a paso moderado", "3.5", "moderada"),
        ("01020", "Bicicleta recreativa", "6.8", "vigorosa"),
        ("12020", "Trotar", "7.0", "vigorosa"),
    ]:
        Actividad.objects.create(codigo_compendium=codigo, nombre=nombre, met=Decimal(met), intensidad=intensidad)


def _imagen(ancho=800, alto=600, formato="JPEG"):
    buffer = BytesIO()
    Image.new("RGB", (ancho, alto), (200, 120, 40)).save(buffer, formato)
    return buffer.getvalue()


@pytest.fixture
def foto_valida():
    return SimpleUploadedFile("comida.jpg", _imagen(), content_type="image/jpeg")


@pytest.fixture
def foto_pequena():
    return SimpleUploadedFile("chica.jpg", _imagen(300, 200), content_type="image/jpeg")


@pytest.fixture
def comida(cliente, catalogo, foto_valida):
    """Comida en borrador creada con el FakeVisionProvider (desde SCRUM-451)."""
    return cliente.post("/api/v1/estimaciones", {"foto": foto_valida}, format="multipart").json()
