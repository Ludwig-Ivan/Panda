from collections.abc import Iterable

import structlog
from django.core.files.storage import default_storage
from django.db import transaction

log = structlog.get_logger(__name__)


def borrar_fotos_al_confirmar(claves: Iterable[str | None]) -> None:
    """Borra objetos de R2 solo si la transacción termina bien (Architecture §7)."""
    pendientes = [c for c in claves if c]
    if not pendientes:
        return

    def _borrar():
        for clave in pendientes:
            try:
                default_storage.delete(clave)
            except Exception:  # noqa: BLE001  el job semanal limpia lo que quede
                log.warning("foto_no_borrada", exc_info=True)

    transaction.on_commit(_borrar)
