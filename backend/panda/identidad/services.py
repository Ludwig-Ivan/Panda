from django.conf import settings
from django.db import IntegrityError, transaction
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from panda.catalogos.models import Actividad
from panda.comun.almacenamiento import borrar_fotos_al_confirmar
from panda.comun.errores import CredencialesInvalidas, EmailTomado, ErrorValidacion, NoEncontrado

from .models import Consentimiento, PreferenciaActividad, Usuario


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


def aceptar_consentimientos(usuario: Usuario, consentimientos: list[dict]) -> None:
    vigentes = versiones_vigentes()
    invalidos = [c for c in consentimientos if vigentes.get(c["tipo"]) != c["version"]]
    if invalidos:
        raise ErrorValidacion(
            "Solo se puede aceptar la versión vigente de cada aviso.",
            details=[{"field": "consentimientos", "issue": "version_no_vigente", "tipo": c["tipo"]} for c in invalidos],
        )
    Consentimiento.objects.bulk_create(
        [Consentimiento(usuario=usuario, tipo=c["tipo"], version=c["version"]) for c in consentimientos],
        ignore_conflicts=True,
    )


def reemplazar_preferencias(usuario: Usuario, actividad_ids: list[int]) -> list[int]:
    ids = list(dict.fromkeys(actividad_ids))  # sin duplicados, conserva el orden
    existentes = set(Actividad.objects.filter(id__in=ids, activo=True).values_list("id", flat=True))
    if len(existentes) != len(ids):
        raise NoEncontrado("Alguna de las actividades elegidas no existe.")
    with transaction.atomic():
        PreferenciaActividad.objects.filter(usuario=usuario).delete()
        PreferenciaActividad.objects.bulk_create([PreferenciaActividad(usuario=usuario, actividad_id=i) for i in ids])
    return ids


def eliminar_cuenta(usuario: Usuario, password: str) -> None:
    """RF-18: borra todo en la BD (cascada) y las fotos en R2 después del commit."""
    if not usuario.check_password(password):
        raise CredencialesInvalidas("La contraseña no es correcta.", status_code=403)
    from panda.comidas.models import Comida  # import local para evitar ciclos entre apps

    with transaction.atomic():
        claves = list(
            Comida.objects.filter(usuario=usuario)
            .exclude(foto__isnull=True)
            .exclude(foto="")
            .values_list("foto", flat=True)
        )
        OutstandingToken.objects.filter(user=usuario).delete()  # ver 0.4, punto 5
        usuario.delete()
        borrar_fotos_al_confirmar(claves)
