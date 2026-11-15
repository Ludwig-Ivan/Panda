import os

os.environ.setdefault("DJANGO_SECRET_KEY", "solo-para-pruebas")
os.environ.setdefault("DATABASE_URL", "postgres://panda:panda@localhost:5432/panda")
os.environ["STORAGE_BACKEND"] = "memory"

from .base import *  # noqa: E402,F401,F403

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # rápido, solo pruebas
CACHES["default"] = {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "panda-test"}  # noqa: F405
PANDA["VISION"]["PROVIDER"] = "panda.estimacion.adaptadores.fake.FakeVisionProvider"  # noqa: F405
