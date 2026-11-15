from urllib.parse import parse_qs, urlparse

from rest_framework.exceptions import NotFound
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

from .errores import SolicitudInvalida


class PaginacionCursor(CursorPagination):
    page_size = 20
    max_page_size = 50
    page_size_query_param = "limit"
    ordering = ("-consumida_at", "-id")

    def decode_cursor(self, request):
        try:
            return super().decode_cursor(request)
        except NotFound as exc:
            raise SolicitudInvalida("El cursor no es válido.") from exc

    def _cursor_opaco(self, enlace):
        if not enlace:
            return None
        return parse_qs(urlparse(enlace).query).get(self.cursor_query_param, [None])[0]

    def get_paginated_response(self, data):
        return Response({"data": data, "meta": {"limit": self.page_size, "next_cursor": self._cursor_opaco(self.get_next_link())}})