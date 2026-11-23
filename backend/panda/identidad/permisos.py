from rest_framework.permissions import BasePermission

from panda.comun.errores import ConsentimientoRequerido, PerfilIncompleto

from . import services
from .models import Perfil


class TienePerfilYConsentimientos(BasePermission):
    """RD-01: crear o corregir comidas exige perfil completo y avisos vigentes aceptados."""

    def has_permission(self, request, view):
        usuario = request.user
        if not usuario or not usuario.is_authenticated:
            return False
        if not Perfil.objects.filter(usuario=usuario).exists():
            raise PerfilIncompleto()
        if services.consentimientos_pendientes(usuario):
            raise ConsentimientoRequerido()
        return True
