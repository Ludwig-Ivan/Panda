# app/vision/imagen.py
"""Validación de la foto por contenido y limpieza de metadatos (T-212).

- Formato por magic bytes (no por extensión ni Content-Type): JPEG, PNG o WebP → si no, 415.
- Más de 10 MB → 413.
- Resolución mínima 640×480 (igual que el backend) → si no, 422.
- Se respeta la orientación EXIF y después se descarta TODO el metadato: la imagen que llega al modelo es un
  lienzo RGB nuevo sin EXIF, GPS ni perfil. La foto vive solo en memoria y nunca se guarda (RNF-SG-09).
"""

import io

from PIL import Image, ImageOps, UnidentifiedImageError

from ..errores import ArchivoMuyGrande, FormatoNoSoportado, ImagenMuyPequena

Image.MAX_IMAGE_PIXELS = 40_000_000  # protege contra bombas de descompresión
FORMATOS = {"JPEG", "PNG", "WEBP"}


def validar_y_limpiar(datos: bytes, max_bytes: int, min_lado_mayor: int, min_lado_menor: int) -> Image.Image:
    if len(datos) > max_bytes:
        raise ArchivoMuyGrande()
    try:
        with Image.open(io.BytesIO(datos)) as original:
            if original.format not in FORMATOS:
                raise FormatoNoSoportado()
            original.load()
            orientada = ImageOps.exif_transpose(original)
            ancho, alto = orientada.size
            if max(ancho, alto) < min_lado_mayor or min(ancho, alto) < min_lado_menor:
                raise ImagenMuyPequena()
            limpia = Image.new("RGB", orientada.size)
            limpia.paste(orientada.convert("RGB"))
            return limpia
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError) as exc:
        raise FormatoNoSoportado() from exc
