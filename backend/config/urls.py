from django.contrib import admin
from django.urls import include, path

from panda.comun.salud import health

urlpatterns = [
    path("health", health),
    path("admin-dev/", admin.site.urls),
    path("api/v1/", include("panda.identidad.urls")),
]
