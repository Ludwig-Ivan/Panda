"""Prueba manual del ia-service, en texto claro (no es la app: la app la hace el frontend).

Modo guiado (te pregunta todo):
    python scripts/probar.py

Modo directo:
    python scripts/probar.py RUTA_A_LA_FOTO.jpg --peso 60 --edad 22 --actividad 1202860
    python scripts/probar.py --kcal 650 --buscar correr

Necesita el servicio corriendo en otra terminal (uvicorn app.main:create_app --factory --port 8100).
"""

import argparse
import os
import sys
import unicodedata
from pathlib import Path

import httpx

NOMBRES = {
    "calorias": "Calorías",
    "masa": "Masa",
    "grasa": "Grasa",
    "carbohidrato": "Carbohidratos",
    "proteina": "Proteína",
}
CAMINAR = "1719060"


def titulo(texto: str) -> None:
    print()
    print("=" * 56)
    print(f"  {texto}")
    print("=" * 56)


def fallo(r: httpx.Response) -> None:
    try:
        detalle = r.json().get("error", r.json())
    except ValueError:
        detalle = r.text
    print(f"  ✗ Error {r.status_code}: {detalle}")


def sin_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


def preguntar(texto: str, defecto: str = "") -> str:
    extra = f" [{defecto}]" if defecto else ""
    try:
        valor = input(f"  {texto}{extra}: ").strip().strip('"').strip("'")
    except EOFError:
        valor = ""
    return valor or defecto


def preguntar_numero(texto: str, defecto: float, minimo: float, maximo: float) -> float:
    while True:
        valor = preguntar(texto, f"{defecto:g}").replace(",", ".")
        try:
            numero = float(valor)
        except ValueError:
            print("  Escribe solo el número.")
            continue
        if minimo <= numero <= maximo:
            return numero
        print(f"  Debe estar entre {minimo:g} y {maximo:g}.")


# ---------------------------------------------------------------- llamadas al servicio


def estado(cliente: httpx.Client) -> bool:
    titulo("Estado del servicio")
    r = cliente.get("/ready")
    for nombre, valor in r.json().get("componentes", {}).items():
        print(f"  {'✓' if valor == 'ok' else '…'} {nombre}: {valor}")
    if r.status_code != 200:
        print("  El servicio aún no está listo; espera unos segundos y vuelve a intentar.")
    return r.status_code == 200


def estimar_foto(cliente: httpx.Client, ruta: Path) -> float | None:
    titulo(f"Estimación de la foto: {ruta.name}")
    with ruta.open("rb") as f:
        r = cliente.post("/v1/vision/estimar", files={"foto": (ruta.name, f)})
    if r.status_code != 200:
        fallo(r)
        return None
    datos = r.json()
    print(f"  Modelo: {datos['modelo']['nombre']} {datos['modelo']['version']}   ({datos['latencia_ms']} ms)")
    print()
    for clave, n in datos["nutrientes"].items():
        print(f"  {NOMBRES.get(clave, clave):<14} {n['valor']:>7} {n['unidad']:<4}  (entre {n['min']} y {n['max']})")
    for aviso in datos.get("avisos", []):
        print(f"  ⓘ {aviso}")
    if datos["modelo"]["nombre"] == "falso":
        print("\n  Nota: IA_MODELO=falso en .env, por eso siempre sale 450 kcal.")
    return float(datos["nutrientes"]["calorias"]["valor"])


def catalogo(cliente: httpx.Client, edad: int) -> list[dict]:
    r = cliente.get("/v1/actividad/catalogo", params={"edad": edad})
    r.raise_for_status()
    return r.json()["actividades"]


def calcular(cliente: httpx.Client, kcal: float, peso: float, edad: int, codigo: str) -> None:
    r = cliente.post("/v1/actividad/calcular", json={"kcal": kcal, "peso_kg": peso, "edad": edad, "codigo": codigo})
    if r.status_code != 200:
        fallo(r)
        return
    act = r.json()
    titulo(f"Para equilibrar {kcal:g} kcal")
    print(f"  Persona:   {peso:g} kg, {edad} años")
    print(f"  Actividad: {act['actividad']}  (MET {act['met']})")
    print(f"  Tiempo:    {act['tiempo']}  ({act['minutos']} min)")
    print(f"  Gasto:     {act['kcal_por_min']} kcal por minuto")
    if act.get("supera_limite_continuo"):
        print("  ⓘ Es mucho tiempo seguido; conviene dividirlo en varias sesiones.")
    for aviso in act.get("avisos", []):
        print(f"  ⓘ {aviso}")


# ---------------------------------------------------------------- elegir actividad


def elegir_actividad(actividades: list[dict], busqueda: str | None = None) -> str | None:
    """Busca por palabra o por categoría y deja escoger por número. Devuelve el código o None para salir."""
    categorias = sorted({a["categoria"] for a in actividades})
    while True:
        if busqueda is None:
            print()
            print("  Categorías: " + ", ".join(categorias))
            busqueda = preguntar("Escribe una palabra o categoría (ej. correr, bici, baile) o Enter para salir")
            if not busqueda:
                return None
        clave = sin_acentos(busqueda)
        encontradas = [
            a for a in actividades if clave in sin_acentos(a["actividad"]) or clave in sin_acentos(a["categoria"])
        ]
        busqueda = None
        if not encontradas:
            print("  No encontré actividades con esa palabra; prueba otra.")
            continue
        print()
        for i, a in enumerate(encontradas, 1):
            print(f"  {i:>3}. {a['actividad']}  (MET {a['met']})")
        opcion = preguntar("Número de la actividad (Enter para buscar otra)")
        if opcion.isdigit() and 1 <= int(opcion) <= len(encontradas):
            return encontradas[int(opcion) - 1]["codigo"]


# ---------------------------------------------------------------- modos


def modo_guiado(cliente: httpx.Client) -> int:
    titulo("¿Cómo quieres registrar la comida?")
    print("  1. Con una foto (la estima el modelo)")
    print("  2. Escribiendo las calorías")
    opcion = preguntar("Opción", "1")

    kcal = None
    if opcion == "2":
        kcal = preguntar_numero("Calorías de la comida", 500, 1, 5000)
    else:
        while kcal is None:
            ruta = Path(preguntar("Arrastra aquí la foto o escribe su ruta"))
            if not ruta.is_file():
                print(f"  No existe la foto: {ruta}")
                continue
            kcal = estimar_foto(cliente, ruta)
            if kcal is None:
                return 1

    titulo("Tus datos")
    peso = preguntar_numero("Peso en kg", 70, 30, 300)
    edad = int(preguntar_numero("Edad", 25, 18, 100))
    actividades = catalogo(cliente, edad)

    while True:
        titulo("Elige la actividad que quieres hacer")
        codigo = elegir_actividad(actividades)
        if codigo is None:
            break
        calcular(cliente, kcal, peso, edad, codigo)
        print()
        if preguntar("¿Probar otra actividad? (s/n)", "s").lower() not in ("s", "si", "sí"):
            break
    print()
    return 0


def modo_directo(cliente: httpx.Client, a: argparse.Namespace) -> int:
    kcal = a.kcal
    if a.foto:
        ruta = Path(a.foto)
        if not ruta.is_file():
            print(f"✗ No existe la foto: {ruta}")
            return 1
        kcal = estimar_foto(cliente, ruta)
        if kcal is None:
            return 1
    codigo = a.actividad
    if a.buscar:
        codigo = elegir_actividad(catalogo(cliente, a.edad), a.buscar)
        if codigo is None:
            return 0
    calcular(cliente, kcal or 500, a.peso, a.edad, codigo or CAMINAR)
    print()
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("foto", nargs="?", help="Ruta a una foto JPG/PNG/WebP (mínimo 640x480)")
    p.add_argument("--kcal", type=float, help="Calorías escritas a mano (en lugar de foto)")
    p.add_argument("--peso", type=float, default=70, help="Peso en kg (default 70)")
    p.add_argument("--edad", type=int, default=25, help="Edad en años (default 25)")
    p.add_argument("--actividad", help="Código de actividad (default caminar)")
    p.add_argument("--buscar", help="Palabra para buscar la actividad y escogerla de una lista")
    p.add_argument("--url", default="http://localhost:8100")
    p.add_argument("--clave", default=os.environ.get("IA_API_KEY", "cambia-esta-clave"))
    a = p.parse_args()

    cliente = httpx.Client(base_url=a.url, headers={"X-API-Key": a.clave}, timeout=120)
    try:
        if not estado(cliente):
            return 1
        directo = a.foto or a.kcal or a.actividad or a.buscar
        return modo_directo(cliente, a) if directo else modo_guiado(cliente)
    except httpx.ConnectError:
        print(f"✗ No me pude conectar a {a.url}. ¿Está corriendo uvicorn en otra terminal?")
        return 1
    except KeyboardInterrupt:
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())
