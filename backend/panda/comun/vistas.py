from django.http import JsonResponse


def _error(status, code, message, request):
    return JsonResponse(
        {"error": {"code": code, "message": message, "details": [], "requestId": getattr(request, "request_id", "")}},
        status=status,
    )


def no_encontrado(request, exception=None):
    return _error(404, "NOT_FOUND", "No encontramos lo que buscas.", request)


def error_servidor(request):
    return _error(500, "INTERNAL_ERROR", "Algo salió mal de nuestro lado. Inténtalo de nuevo en unos minutos.", request)
