from django.http import HttpResponse
from django.test import RequestFactory

from panda.comun.middleware import RequestIdMiddleware
from panda.comun.paginacion import PaginacionCursor
from panda.comun.throttles import LoginRateThrottle


def _middleware():
    return RequestIdMiddleware(lambda request: HttpResponse("ok"))


def test_respeta_un_request_id_valido():
    r = _middleware()(RequestFactory().get("/health", HTTP_X_REQUEST_ID="abc-123"))
    assert r["X-Request-Id"] == "abc-123"


def test_reemplaza_un_request_id_invalido():
    r = _middleware()(RequestFactory().get("/health", HTTP_X_REQUEST_ID="<script>"))
    assert r["X-Request-Id"] != "<script>" and len(r["X-Request-Id"]) == 16


def test_tasa_con_ventana_en_segundos():
    assert LoginRateThrottle().parse_rate("10/900s") == (10, 900)


def test_cursor_opaco_extrae_solo_el_token():
    paginador = PaginacionCursor()
    assert paginador._cursor_opaco("http://x/api/v1/comidas?cursor=cD0yMDI2&limit=1") == "cD0yMDI2"
    assert paginador._cursor_opaco(None) is None
