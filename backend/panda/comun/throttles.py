from rest_framework.throttling import SimpleRateThrottle


class _VentanaEnSegundos(SimpleRateThrottle):
    """Permite tasas como '10/900s' (10 cada 15 min), que DRF no admite de serie."""

    def parse_rate(self, rate):
        if rate is None:
            return None, None
        numero, periodo = rate.split("/")
        return int(numero), int(periodo.rstrip("s"))


class LoginRateThrottle(_VentanaEnSegundos):
    scope = "login"

    def get_cache_key(self, request, view):
        email = str(request.data.get("email", "")).strip().lower()
        return self.cache_format % {"scope": self.scope, "ident": f"{self.get_ident(request)}:{email}"}


class RegistroRateThrottle(_VentanaEnSegundos):
    scope = "registro"

    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}
