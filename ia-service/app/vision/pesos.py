# app/vision/pesos.py
"""Descarga y verificación de `best.pt` al arrancar (T-210).

Regla: el servicio NUNCA carga pesos cuyo SHA-256 no coincida con IA_MODELO_SHA256. Si el archivo ya está en
IA_MODELO_DIR y coincide, no se descarga de nuevo (arranques rápidos con un volumen persistente).
"""

import hashlib
import logging
import os
import shutil
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

import httpx

log = logging.getLogger("ia.pesos")
BLOQUE = 1024 * 1024


class ErrorPesos(RuntimeError):
    """Los pesos no están disponibles o no coinciden con el SHA-256 esperado."""


def sha256_de(ruta: Path) -> str:
    h = hashlib.sha256()
    with Path(ruta).open("rb") as f:
        for bloque in iter(lambda: f.read(BLOQUE), b""):
            h.update(bloque)
    return h.hexdigest()


def ruta_de_file_url(url: str) -> Path:
    """Convierte una URL file:// en ruta local, también en Windows.

    Acepta la forma correcta (file:///C:/modelos/best.pt, la que da Path.as_uri()) y la que se suele escribir a mano
    (file://C:\\modelos\\best.pt). urlparse no sirve: en la segunda toma «C:» como servidor y deja la ruta vacía.
    """
    resto = url[len("file://") :]
    if resto.startswith("localhost/"):
        resto = resto[len("localhost") :]
    return Path(url2pathname(unquote(resto)) if resto.startswith("/") else resto)


def _descargar(url: str, destino: Path, cliente: httpx.Client | None) -> None:
    if url.startswith("file://"):  # desarrollo local y pruebas
        origen = ruta_de_file_url(url)
        if not origen.is_file():
            raise ErrorPesos(f"No existe el archivo de pesos {origen}")
        shutil.copyfile(origen, destino)
        return
    partes = urlparse(url)
    if partes.scheme != "https":
        raise ErrorPesos("IA_MODELO_URL debe usar https:// (o file:// en desarrollo)")
    propio = cliente is None
    cliente = cliente or httpx.Client(timeout=httpx.Timeout(30.0, read=300.0), follow_redirects=True)
    try:
        with cliente.stream("GET", url) as r:
            r.raise_for_status()
            with destino.open("wb") as f:
                for bloque in r.iter_bytes(BLOQUE):
                    f.write(bloque)
    except httpx.HTTPError as exc:
        raise ErrorPesos(f"No se pudieron descargar los pesos: {type(exc).__name__}") from exc
    finally:
        if propio:
            cliente.close()


def asegurar_pesos(
    directorio: Path, archivo: str, sha256: str | None, url: str | None, cliente: httpx.Client | None = None
) -> Path:
    if not sha256:
        raise ErrorPesos("Falta IA_MODELO_SHA256: no se cargan pesos sin verificar")
    directorio = Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    ruta = directorio / archivo

    if ruta.exists():
        if sha256_de(ruta) == sha256:
            log.info("pesos_verificados origen=cache")
            return ruta
        log.warning("pesos_en_cache_no_coinciden: se descargan de nuevo")

    if not url:
        raise ErrorPesos(f"No existe {ruta} y falta IA_MODELO_URL para descargarlo")

    fd, temporal = tempfile.mkstemp(dir=directorio, suffix=".parcial")
    os.close(fd)
    temporal_path = Path(temporal)
    try:
        _descargar(url, temporal_path, cliente)
        obtenido = sha256_de(temporal_path)
        if obtenido != sha256:
            raise ErrorPesos(f"SHA-256 no coincide: esperado {sha256[:12]}…, obtenido {obtenido[:12]}…")
        temporal_path.replace(ruta)  # atómico: nunca queda un best.pt a medias
    finally:
        temporal_path.unlink(missing_ok=True)
    log.info("pesos_verificados origen=descarga")
    return ruta
