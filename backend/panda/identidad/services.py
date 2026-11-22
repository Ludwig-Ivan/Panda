from django.conf import settings
from django.db import IntegrityError, transaction

from panda.comun.errores import EmailTomado

from .models import Consentimiento, Usuario


def versiones_vigentes() -> dict[str, str]:
    return settings.PANDA["CONSENTIMIENTOS_VIGENTES"]


def consentimientos_faltantes(aceptados: set[tuple[str, str]]) -> list[str]:
    return [tipo for tipo, version in versiones_vigentes().items() if (tipo, version) not in aceptados]


def consentimientos_pendientes(usuario: Usuario) -> list[str]:
    aceptados = set(Consentimiento.objects.filter(usuario=usuario).values_list("tipo", "version"))
    return consentimientos_faltantes(aceptados)


def registrar_usuario(*, email: str, password: str, mayor_edad: bool, consentimientos: list[dict]) -> Usuario:
    try:
        with transaction.atomic():
            usuario = Usuario.objects.create_user(email=email, password=password, mayor_edad_declarado=mayor_edad)
            Consentimiento.objects.bulk_create(
                [Consentimiento(usuario=usuario, tipo=c["tipo"], version=c["version"]) for c in consentimientos],
                ignore_conflicts=True,
            )
    except IntegrityError as exc:  # dos registros simultáneos con el mismo correo
        raise EmailTomado() from exc
    return usuario
