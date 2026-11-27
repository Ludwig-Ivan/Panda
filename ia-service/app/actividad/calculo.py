# app/actividad/calculo.py
"""Fórmula del ADR (T-221): kcal/min = (MET − 1) × K × peso / 200 en modo neto, o MET × K × peso / 200 en bruto.

K = 3.5 para menores de 60 años y 2.7 para 60 o más. Es la misma fórmula de la sección 11 del notebook.
Sin Django ni FastAPI: funciones puras y fáciles de probar.
"""

from decimal import ROUND_HALF_UP, Decimal

from .compendio import EDAD_ADULTO_MAYOR, K_ADULTOS, K_MAYORES

LIMITE_CONTINUO_MIN = 90  # RF-14: duración máxima recomendada de una sola sesión
MET_VIGOROSO = 6.0


def factor_o2(edad: int) -> float:
    return K_MAYORES if edad >= EDAD_ADULTO_MAYOR else K_ADULTOS


def kcal_por_minuto(met: float, peso_kg: float, edad: int, neto: bool = True) -> float:
    if peso_kg <= 0:
        raise ValueError("El peso debe ser positivo")
    efectivo = met - 1 if neto else met
    if efectivo <= 0:
        raise ValueError("En modo neto la actividad debe tener un MET mayor que 1")
    return efectivo * factor_o2(edad) * peso_kg / 200


def redondear(valor: float) -> int:
    """Redondeo half-up (round() de Python es bancario: 50.5 → 50)."""
    return int(Decimal(str(valor)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def minutos(kcal: float, met: float, peso_kg: float, edad: int, neto: bool = True) -> int:
    return redondear(kcal / kcal_por_minuto(met, peso_kg, edad, neto))


def texto_tiempo(total_min: int) -> str:
    h, m = divmod(total_min, 60)
    return f"{h} h {m} min" if h else f"{m} min"
