from django.conf import settings
from django.core.files.storage import default_storage
from django.db import connection
from django.http import JsonResponse


def health(request):
    checks = {}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception:  # noqa: BLE001
        checks["database"] = "error"
    try:
        default_storage.exists("health/ping")
        checks["storage"] = "ok"
    except Exception:  # noqa: BLE001
        checks["storage"] = "degraded"

    from panda.estimacion.resiliencia import estado_vision
    checks["vision"] = estado_vision()

    ok = checks["database"] == "ok"
    return JsonResponse(
        {"status": "ok" if ok else "error", "version": settings.APP_VERSION, "checks": checks},
        status=200 if ok else 503,
    )