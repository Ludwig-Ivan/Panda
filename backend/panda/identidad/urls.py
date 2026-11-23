# panda/identidad/urls.py  (versión final)
from django.urls import path

from . import views

urlpatterns = [
    path("auth/registro", views.RegistroView.as_view()),
    path("auth/login", views.LoginView.as_view()),
    path("auth/refresh", views.RefreshView.as_view()),
    path("auth/logout", views.LogoutView.as_view()),
    path("usuarios/me", views.UsuarioMeView.as_view()),
    path("consentimientos", views.ConsentimientosView.as_view()),
    path("perfil", views.PerfilView.as_view()),
    path("perfil/preferencias-actividad", views.PreferenciasView.as_view()),
]
