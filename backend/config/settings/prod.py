import sentry_sdk

from .base import *  # noqa: F401,F403

DEBUG = False
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r"^health$"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])  # noqa: F405
ADMIN_REQUIERE_OTP = True
STORAGES["staticfiles"] = {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}  # noqa: F405

if SENTRY_DSN := env("SENTRY_DSN", default=""):  # noqa: F405
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENV,  # noqa: F405
        release=APP_VERSION,  # noqa: F405
        send_default_pii=False,  # nunca correos ni IPs
        traces_sample_rate=0.1,
    )
