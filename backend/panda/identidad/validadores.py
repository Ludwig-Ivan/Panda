import re

from django.core.exceptions import ValidationError


class LetraYNumeroValidator:
    def validate(self, password, user=None):
        if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            raise ValidationError(
                "La contraseña debe tener al menos una letra y un número.", code="password_letra_numero"
            )

    def get_help_text(self):
        return "Tu contraseña debe incluir al menos una letra y un número."
