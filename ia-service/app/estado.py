# app/estado.py
"""Estado de carga de los modelos. /ready responde 503 hasta que todo está listo (T-204)."""

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

log = logging.getLogger("ia.estado")


@dataclass
class Estado:
    componentes: dict[str, Any] = field(default_factory=dict)
    errores: dict[str, str] = field(default_factory=dict)
    pendientes: set[str] = field(default_factory=set)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    @property
    def listo(self) -> bool:
        with self._lock:
            return not self.pendientes and not self.errores

    def obtener(self, nombre: str) -> Any | None:
        with self._lock:
            return self.componentes.get(nombre)

    def resumen(self) -> dict[str, str]:
        with self._lock:
            salida = {n: "ok" for n in self.componentes}
            salida |= {n: "cargando" for n in self.pendientes}
            salida |= {n: "error" for n in self.errores}  # el detalle va a los logs, no a la respuesta
            return salida

    def cargar(self, nombre: str, fabrica: Callable[[], Any], en_segundo_plano: bool = True) -> None:
        """Ejecuta `fabrica` y guarda el resultado. En segundo plano para que /health responda mientras carga."""
        with self._lock:
            self.pendientes.add(nombre)
            self.errores.pop(nombre, None)

        def _tarea() -> None:
            inicio = time.monotonic()
            try:
                valor = fabrica()
            except Exception as exc:  # noqa: BLE001  se registra y /ready queda en 503
                log.exception("carga_fallida componente=%s", nombre)
                with self._lock:
                    self.pendientes.discard(nombre)
                    self.errores[nombre] = type(exc).__name__
                return
            with self._lock:
                self.componentes[nombre] = valor
                self.pendientes.discard(nombre)
            log.info("componente_listo componente=%s segundos=%.1f", nombre, time.monotonic() - inicio)

        if en_segundo_plano:
            threading.Thread(target=_tarea, name=f"carga-{nombre}", daemon=True).start()
        else:
            _tarea()
