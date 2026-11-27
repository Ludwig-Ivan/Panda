# app/limite.py
"""Límite de tamaño de la petición antes de que FastAPI lea el cuerpo (T-206).

Rechaza con 413 por Content-Length y, si no viene (transferencia por partes), cuenta los bytes conforme llegan.
Así una petición enorme nunca termina en memoria ni en un archivo temporal.
"""

import json

from starlette.types import ASGIApp, Message, Receive, Scope, Send

_CUERPO_413 = json.dumps(
    {"error": {"code": "PAYLOAD_TOO_LARGE", "message": "La foto pesa más de 10 MB.", "details": []}}
).encode()


class LimiteTamano:
    def __init__(self, app: ASGIApp, max_bytes: int):
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        cabeceras = dict(scope.get("headers") or [])
        longitud = cabeceras.get(b"content-length")
        if longitud is not None:
            try:
                if int(longitud) > self.max_bytes:
                    await self._responder_413(send)
                    return
            except ValueError:
                pass
            await self.app(scope, receive, send)
            return

        # Sin Content-Length: se lee el cuerpo contando bytes y luego se entrega a la app.
        mensajes: list[Message] = []
        total = 0
        while True:
            mensaje = await receive()
            mensajes.append(mensaje)
            if mensaje["type"] == "http.request":
                total += len(mensaje.get("body", b""))
                if total > self.max_bytes:
                    await self._responder_413(send)
                    return
                if not mensaje.get("more_body", False):
                    break
            else:
                break

        async def reproducir() -> Message:
            return mensajes.pop(0) if mensajes else {"type": "http.disconnect"}

        await self.app(scope, reproducir, send)

    @staticmethod
    async def _responder_413(send: Send) -> None:
        cabeceras = [(b"content-type", b"application/json"), (b"content-length", str(len(_CUERPO_413)).encode())]
        await send({"type": "http.response.start", "status": 413, "headers": cabeceras})
        await send({"type": "http.response.body", "body": _CUERPO_413})
