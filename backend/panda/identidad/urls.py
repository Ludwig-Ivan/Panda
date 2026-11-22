from django.urls import path

from . import views

urlpatterns = [
    path("auth/registro", views.RegistroView.as_view()),
    path("auth/login", views.LoginView.as_view()),
    path("auth/refresh", views.RefreshView.as_view()),
    path("auth/logout", views.LogoutView.as_view()),
]
