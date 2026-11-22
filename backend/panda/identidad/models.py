import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


# Enumeraciones a nivel de módulo (ver 0.4, punto 1)
class Sexo(models.TextChoices):
    FEMENINO = "femenino", "Femenino"
    MASCULINO = "masculino", "Masculino"
    NO_INDICA = "no_indica", "Prefiero no indicar"


class NivelActividad(models.TextChoices):
    SEDENTARIO = "sedentario", "Sedentario"
    LIGERO = "ligero", "Ligero"
    MODERADO = "moderado", "Moderado"
    ALTO = "alto", "Alto"


class TipoConsentimiento(models.TextChoices):
    PRIVACIDAD = "privacidad", "Aviso de privacidad"
    AVISOS_SALUD = "avisos_salud", "Avisos de salud"
    PROCESAMIENTO_TERCEROS = "procesamiento_terceros", "Procesamiento por terceros"


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def _crear(self, email, password, **extra):
        if not email:
            raise ValueError("El correo es obligatorio")
        usuario = self.model(email=self.normalize_email(email).lower(), **extra)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._crear(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.update(is_staff=True, is_superuser=True, mayor_edad_declarado=True)
        return self._crear(email, password, **extra)


class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=254, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    mayor_edad_declarado = models.BooleanField()
    guardar_fotos = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []  # type: ignore[misc]  # django-stubs lo declara ClassVar

    class Meta:
        db_table = "usuarios"
        constraints = [
            models.CheckConstraint(condition=Q(email=Lower("email")), name="ck_usuarios_email_minusculas"),
            models.CheckConstraint(condition=Q(mayor_edad_declarado=True), name="ck_usuarios_mayor_edad"),
        ]

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)  # no exponer el correo en logs ni en el admin


class Perfil(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True, related_name="perfil")
    edad = models.SmallIntegerField()
    sexo = models.CharField(max_length=10, choices=Sexo.choices)
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2)
    estatura_cm = models.DecimalField(max_digits=5, decimal_places=1)
    nivel_actividad = models.CharField(max_length=10, choices=NivelActividad.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "perfiles"
        constraints = [
            models.CheckConstraint(condition=Q(edad__gte=18, edad__lte=100), name="ck_perfiles_edad"),
            models.CheckConstraint(condition=Q(peso_kg__gte=30, peso_kg__lte=300), name="ck_perfiles_peso"),
            models.CheckConstraint(
                condition=Q(estatura_cm__gte=120, estatura_cm__lte=230), name="ck_perfiles_estatura"
            ),
            models.CheckConstraint(condition=Q(sexo__in=Sexo.values), name="ck_perfiles_sexo"),
            models.CheckConstraint(condition=Q(nivel_actividad__in=NivelActividad.values), name="ck_perfiles_nivel"),
        ]


class Consentimiento(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="consentimientos")
    tipo = models.CharField(max_length=25, choices=TipoConsentimiento.choices)
    version = models.CharField(max_length=20)
    aceptado_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "consentimientos"
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "tipo", "version"], name="uq_consentimientos_usuario_tipo_version"
            ),
            models.CheckConstraint(condition=Q(tipo__in=TipoConsentimiento.values), name="ck_consentimientos_tipo"),
        ]


class PreferenciaActividad(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="preferencias_actividad")
    actividad = models.ForeignKey("catalogos.Actividad", on_delete=models.PROTECT, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "preferencias_actividad"
        constraints = [models.UniqueConstraint(fields=["usuario", "actividad"], name="uq_preferencias_actividad")]
