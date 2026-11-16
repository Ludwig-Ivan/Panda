import re
import unicodedata


def normalizar(texto: str) -> str:
    """'  Frijoles  de la OLLA ' -> 'frijoles de la olla'; 'Jamón' -> 'jamon'."""
    sin_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", sin_acentos.lower()).strip()
