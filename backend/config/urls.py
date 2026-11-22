from django.contrib import admin
from django.urls import path

from panda.comun.salud import health

urlpatterns = [path("health", health), path("admin-dev/", admin.site.urls)]
