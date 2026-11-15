from datetime import timedelta
from pathlib import Path
from typing import Any

import environ
import structlog
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

# --- General -------------------------------------------------------------
ENV = env("ENV", default="development")
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
APP_VERSION = env("APP_VERSION", default="0.1.0")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # Terceros
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "corsheaders",
    "storages",
    "django_otp",
    "django_otp.plugins.otp_totp",
    # Panda
    "panda.comun",
    "panda.identidad",
    "panda.catalogos",
    "panda.comidas",
    "panda.estimacion",
    "panda.recomendacion",
]

MIDDLEWARE = [
    "panda.comun.middleware.RequestIdMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- Base de datos -------------------------------------------------------
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["CONN_MAX_AGE"] = 60
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Usuarios y contraseñas ---------------------------------------------
AUTH_USER_MODEL = "identidad.Usuario" 
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "panda.identidad.validadores.LetraYNumeroValidator"},
]

# --- Internacionalización -----------------------------------------------
LANGUAGE_CODE = "es-mx"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Estáticos y archivos -------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGE_BACKEND = env("STORAGE_BACKEND", default="local")
if STORAGE_BACKEND == "r2":
    R2_ACCOUNT_ID = env("R2_ACCOUNT_ID")
    _storage_default = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": env("R2_BUCKET"),
            "endpoint_url": f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
            "access_key": env("R2_ACCESS_KEY_ID"),
            "secret_key": env("R2_SECRET_ACCESS_KEY"),
            "region_name": "auto",
            "signature_version": "s3v4",
            "default_acl": None,          # R2 no usa ACL; el bucket es privado
            "querystring_auth": True,     # URLs prefirmadas
            "querystring_expire": 600,    # 10 minutos
            "file_overwrite": True,       # la clave ya es única (UUID de la comida)
            "object_parameters": {"ContentType": "image/webp", "CacheControl": "private, max-age=600"},
        },
    }
elif STORAGE_BACKEND == "local":
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"
    _storage_default = {"BACKEND": "django.core.files.storage.FileSystemStorage"}
else:  # "memory": pruebas
    _storage_default = {"BACKEND": "django.core.files.storage.InMemoryStorage"}

STORAGES = {
    "default": _storage_default,
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# Límites de carga (API Specification §8)
DATA_UPLOAD_MAX_MEMORY_SIZE = 65_536          # 64 KB para cuerpos que no son archivos
FILE_UPLOAD_MAX_MEMORY_SIZE = 2_621_440       # > 2.5 MB se escribe a disco temporal

# --- Caché ---------------------------------------------------------------
CACHES = {
    # Compartida entre workers: throttling e idempotencia
    "default": {"BACKEND": "django.core.cache.backends.db.DatabaseCache", "LOCATION": "django_cache"},
    # Por proceso: catálogo de actividades
    "local": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "panda-local", "TIMEOUT": 600},
}

# --- Django REST Framework ----------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["djangorestframework_camel_case.render.CamelCaseJSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["djangorestframework_camel_case.parser.CamelCaseJSONParser"],
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.UserRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {
        "user": "60/min",
        "anon": "60/min",
        "estimaciones": "5/min",
        "login": "10/900s",
        "registro": "10/900s",
    },
    "EXCEPTION_HANDLER": "panda.comun.errores.manejar_excepcion",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "COERCE_DECIMAL_TO_STRING": False,   # los Decimal salen como números JSON
}

# --- JWT -----------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": env("JWT_SIGNING_KEY", default=SECRET_KEY),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_HEADER_TYPES": ("Bearer",),
}
AUTH_COOKIE = {
    "NOMBRE": "panda_rt",
    "PATH": "/api/v1/auth",
    "SECURE": env.bool("AUTH_COOKIE_SECURE", default=True),
    "SAMESITE": "Strict",
}

# --- OpenAPI -------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "Panda API",
    "VERSION": "1.0.0",
    "DESCRIPTION": "API del MVP de Panda para estimar calorías a partir de una foto y recomendar actividad física.",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/v1",
    "SCHEMA_PATH_PREFIX_TRIM": True,
    "SERVERS": [
        {"url": "http://localhost:8000/api/v1", "description": "Desarrollo"},
        {"url": "https://api.panda.app/api/v1", "description": "Producción (provisional)"},
    ],
    "COMPONENT_SPLIT_REQUEST": True,
    
    "ENUM_NAME_OVERRIDES": {
        "EstadoComidaEnum": "panda.comidas.models.EstadoComida",
        "OrigenComidaEnum": "panda.comidas.models.OrigenComida",
        "OrigenItemEnum": "panda.comidas.models.OrigenItem",
        "EstadoConfirmarEnum": [("confirmada", "Confirmada")],
        "TipoConsentimientoEnum": "panda.identidad.models.TipoConsentimiento",
        "TipoCorreccionEnum": "panda.comidas.models.TipoCorreccion",
    },
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
        "drf_spectacular.hooks.postprocess_schema_enums",
    ],
}

# --- CORS y seguridad común ----------------------------------------------
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = (*default_headers, "idempotency-key", "x-request-id", "x-confirm")
CORS_EXPOSE_HEADERS = ["x-request-id", "location", "retry-after"]

APPEND_SLASH = False                 # rutas sin barra final (API §2)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
ADMIN_URL = env("ADMIN_URL", default="admin-dev/")
ADMIN_REQUIERE_OTP = env.bool("ADMIN_REQUIERE_OTP", default=False)

# --- Parámetros del negocio (RNF-MA-04: fuera del código) -----------------
PANDA: dict[str, Any] = {   # anotado para que mypy permita settings.PANDA["..."]["..."]
    "CONSENTIMIENTOS_VIGENTES": {
        "privacidad": env("CONSENT_PRIVACIDAD", default="2026-10"),
        "avisos_salud": env("CONSENT_AVISOS_SALUD", default="2026-10"),
        "procesamiento_terceros": env("CONSENT_TERCEROS", default="2026-10"),
    },
    "AVISOS": [
        "Las calorías son una estimación aproximada a partir de la foto.",
        "Panda no sustituye la orientación de un profesional de la salud o la nutrición.",
    ],
    "ESTIMACION": {
        "CONFIANZA_MINIMA": env.float("CONFIANZA_MINIMA", default=0.30),
        "CONFIANZA_REVISION": 0.50,
        "SIMILITUD_MINIMA": env.float("SIMILITUD_MINIMA", default=0.40),
        "MAX_FOTO_BYTES": 10 * 1024 * 1024,
        "MIN_LADO_MAYOR": 640,
        "MIN_LADO_MENOR": 480,
        "LADO_MAXIMO": 1280,
        "LIMITE_DIARIO": env.int("LIMITE_DIARIO_ESTIMACIONES", default=30),
        "MAX_ITEMS": 20,
    },
    "RECOMENDACION": {
        "MAX_CONTINUA_MIN": env.int("REC_MAX_CONTINUA_MIN", default=90),
        "SESION_FRACCION_MIN": 45,
        "MAX_TOTAL_MIN": 180,
        "MAX_ACTIVIDADES": 5,
        "MINIMO_DESEADO": 3,
    },
    "VISION": {
        "PROVIDER": env("VISION_PROVIDER", default="panda.estimacion.adaptadores.fake.FakeVisionProvider"),
        "PRESUPUESTO_S": 13.0,
        "MIN_RESTANTE_REINTENTO_S": 3.0,
        "REINTENTOS": 1,
        "CB_FALLOS": 5,
        "CB_VENTANA_S": 60,
        "CB_PAUSA_S": 30,
    },
    "BORRADOR_TTL_HORAS": 24,
}

# --- Logs estructurados (RNF-SG-11: sin datos personales) -----------------
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", default="INFO")},
}