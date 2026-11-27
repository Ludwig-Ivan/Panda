"""Conecta el modelo real (best.pt) al servicio en un solo paso, sin Colab.

Descarga best.pt desde una URL (por defecto, el de Drive de Estefanía), lo guarda en la caché
del servicio, calcula su SHA-256 y actualiza el .env con IA_MODELO=siglip y la URL/SHA.

Uso (desde ia-service/, con el venv activado y uvicorn APAGADO):
    python scripts/conectar_modelo.py
    python scripts/conectar_modelo.py --url https://huggingface.co/USUARIO/REPO/resolve/main/best.pt

Después solo arranca uvicorn: como best.pt ya está en la caché con el SHA correcto, no se descarga otra vez.
"""

import argparse
import hashlib
import html
import os
import re
import sys
import tempfile
from pathlib import Path

import httpx

DRIVE_ID = "1ZH0uFjL3yPI634PFCmPDxBS_d0x7Ft6d"
URL_DRIVE = f"https://drive.usercontent.google.com/download?id={DRIVE_ID}&export=download&confirm=t"
RAIZ = Path(__file__).resolve().parents[1]
ENV = RAIZ / ".env"
CACHE_DEFECTO = Path("C:/modelos/cache") if os.name == "nt" else Path.home() / "modelos" / "cache"


def url_de_confirmacion(pagina: str) -> str | None:
    """Drive a veces responde con el aviso "no se pudo analizar en busca de virus": un <form> con campos ocultos."""
    accion = re.search(r'<form[^>]+action="([^"]+)"', pagina)
    if not accion:
        return None
    campos = dict(re.findall(r'<input[^>]+name="([^"]+)"[^>]+value="([^"]*)"', pagina))
    if "id" not in campos:
        return None
    return str(httpx.URL(html.unescape(accion.group(1)), params=campos))


def descargar(url: str, destino: Path, intento: int = 0) -> str:
    """Descarga en streaming, muestra el avance y devuelve el SHA-256. Nunca deja un archivo a medias."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=destino.parent, suffix=".parcial")
    os.close(fd)
    tmp_path = Path(tmp)
    h = hashlib.sha256()
    try:
        with httpx.stream("GET", url, follow_redirects=True, timeout=httpx.Timeout(30.0, read=300.0)) as r:
            r.raise_for_status()
            if "text/html" in r.headers.get("content-type", ""):
                siguiente = url_de_confirmacion(r.read().decode("utf-8", "replace")) if intento == 0 else None
                if siguiente:
                    print("  Drive pidió confirmar la descarga de un archivo grande; confirmando…")
                    tmp_path.unlink(missing_ok=True)
                    return descargar(siguiente, destino, intento + 1)
                raise SystemExit(
                    "✗ Drive devolvió una página web en lugar del archivo.\n"
                    "  Revisa que best.pt esté compartido como 'Cualquier persona con el enlace'."
                )
            total = int(r.headers.get("content-length", 0))
            hecho = 0
            with tmp_path.open("wb") as f:
                for bloque in r.iter_bytes(1024 * 1024):
                    f.write(bloque)
                    h.update(bloque)
                    hecho += len(bloque)
                    if total:
                        print(f"\r  Descargando… {hecho / 1e6:6.0f} / {total / 1e6:.0f} MB", end="", flush=True)
                    else:
                        print(f"\r  Descargando… {hecho / 1e6:6.0f} MB", end="", flush=True)
        print()
        if hecho < 1_000_000:
            raise SystemExit(f"✗ El archivo descargado pesa solo {hecho} bytes; no parece ser best.pt.")
        tmp_path.replace(destino)
    except httpx.HTTPError as exc:
        raise SystemExit(f"✗ No se pudo descargar: {type(exc).__name__}: {exc}") from exc
    finally:
        tmp_path.unlink(missing_ok=True)
    return h.hexdigest()


def actualizar_env(valores: dict[str, str]) -> None:
    lineas = ENV.read_text(encoding="utf-8").splitlines() if ENV.exists() else []
    pendientes = dict(valores)
    nuevas = []
    for linea in lineas:
        clave = linea.split("=", 1)[0].strip().lstrip("# ").strip()
        if clave in pendientes and "=" in linea:
            nuevas.append(f"{clave}={pendientes.pop(clave)}")
        else:
            nuevas.append(linea)
    nuevas += [f"{k}={v}" for k, v in pendientes.items()]
    ENV.write_text("\n".join(nuevas) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--url", default=URL_DRIVE, help="URL https de best.pt (por defecto, Drive)")
    p.add_argument("--cache", type=Path, default=CACHE_DEFECTO, help=f"Carpeta de caché (default {CACHE_DEFECTO})")
    a = p.parse_args()

    if not a.url.startswith("https://"):
        print("✗ La URL debe empezar con https://")
        return 1

    destino = a.cache / "best.pt"
    print(f"1/3  Descargando best.pt a {destino}")
    sha = descargar(a.url, destino)

    print(f"2/3  SHA-256: {sha}")

    actualizar_env(
        {
            "IA_MODELO": "siglip",
            "IA_MODELO_URL": a.url,
            "IA_MODELO_SHA256": sha,
            "IA_MODELO_DIR": a.cache.as_posix(),
            "IA_MODELO_ARCHIVO": "best.pt",
        }
    )
    print(f"3/3  .env actualizado ({ENV})")
    print()
    print("✓ Listo. Ahora arranca el servicio:")
    print("    uvicorn app.main:create_app --factory --port 8100")
    print("  y prueba:  python scripts\\probar.py RUTA_DE_LA_FOTO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
