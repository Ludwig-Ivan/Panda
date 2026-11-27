# tests/test_pesos.py
"""T-210: el servicio descarga y verifica los pesos al arrancar, y nunca carga un archivo que no coincide."""

import hashlib

import httpx
import pytest

from app.vision.pesos import ErrorPesos, asegurar_pesos

CONTENIDO = b"pesos-de-prueba" * 1000
SHA = hashlib.sha256(CONTENIDO).hexdigest()


def _cliente(contenido=CONTENIDO, status=200, llamadas=None):
    def manejar(request):
        if llamadas is not None:
            llamadas.append(str(request.url))
        return httpx.Response(status, content=contenido)

    return httpx.Client(transport=httpx.MockTransport(manejar))


def test_descarga_y_verifica(tmp_path):
    ruta = asegurar_pesos(tmp_path, "best.pt", SHA, "https://ejemplo/best.pt", cliente=_cliente())
    assert ruta.read_bytes() == CONTENIDO
    assert not list(tmp_path.glob("*.parcial"))


def test_no_vuelve_a_descargar_si_el_archivo_coincide(tmp_path):
    (tmp_path / "best.pt").write_bytes(CONTENIDO)
    llamadas = []
    asegurar_pesos(tmp_path, "best.pt", SHA, "https://ejemplo/best.pt", cliente=_cliente(llamadas=llamadas))
    assert llamadas == []


def test_reemplaza_un_archivo_corrupto_en_cache(tmp_path):
    (tmp_path / "best.pt").write_bytes(b"corrupto")
    ruta = asegurar_pesos(tmp_path, "best.pt", SHA, "https://ejemplo/best.pt", cliente=_cliente())
    assert ruta.read_bytes() == CONTENIDO


def test_sha_distinto_no_deja_archivo(tmp_path):
    with pytest.raises(ErrorPesos, match="SHA-256 no coincide"):
        asegurar_pesos(tmp_path, "best.pt", SHA, "https://ejemplo/best.pt", cliente=_cliente(b"otro"))
    assert not (tmp_path / "best.pt").exists() and not list(tmp_path.glob("*.parcial"))


def test_sin_sha_configurado_no_carga_nada(tmp_path):
    with pytest.raises(ErrorPesos, match="IA_MODELO_SHA256"):
        asegurar_pesos(tmp_path, "best.pt", None, "https://ejemplo/best.pt")


def test_sin_archivo_ni_url(tmp_path):
    with pytest.raises(ErrorPesos, match="IA_MODELO_URL"):
        asegurar_pesos(tmp_path, "best.pt", SHA, None)


def test_error_http_se_reporta(tmp_path):
    with pytest.raises(ErrorPesos, match="descargar"):
        asegurar_pesos(tmp_path, "best.pt", SHA, "https://ejemplo/best.pt", cliente=_cliente(status=404))


def test_solo_https_o_file(tmp_path):
    with pytest.raises(ErrorPesos, match="https"):
        asegurar_pesos(tmp_path, "best.pt", SHA, "http://ejemplo/best.pt")


@pytest.mark.parametrize("como", ["as_uri", "a_mano"])
def test_file_url_para_desarrollo(tmp_path, como):
    origen = tmp_path / "origen.pt"
    origen.write_bytes(CONTENIDO)
    # as_uri da file:///C:/... en Windows; a mano se suele escribir file://C:\... — ambas deben funcionar
    url = origen.as_uri() if como == "as_uri" else f"file://{origen}"
    ruta = asegurar_pesos(tmp_path / "cache", "best.pt", SHA, url)
    assert ruta.read_bytes() == CONTENIDO


def test_file_url_inexistente(tmp_path):
    with pytest.raises(ErrorPesos, match="No existe"):
        asegurar_pesos(tmp_path, "best.pt", SHA, (tmp_path / "no_esta.pt").as_uri())


@pytest.mark.parametrize(
    ("url", "esperada"),
    [
        ("file:///C:/modelos/best.pt", "C:/modelos/best.pt"),
        ("file://C:\\modelos\\best.pt", "C:\\modelos\\best.pt"),
        ("file:///home/ia/best.pt", "/home/ia/best.pt"),
        ("file://localhost/home/ia/best.pt", "/home/ia/best.pt"),
    ],
)
def test_ruta_de_file_url(url, esperada, monkeypatch):
    import app.vision.pesos as pesos

    # url2pathname depende del sistema; se fija el comportamiento de Windows para "/C:/..." y POSIX para lo demás
    monkeypatch.setattr(pesos, "url2pathname", lambda r: r[1:] if r[2:3] == ":" else r)
    assert str(pesos.ruta_de_file_url(url)).replace("\\", "/") == esperada.replace("\\", "/")
