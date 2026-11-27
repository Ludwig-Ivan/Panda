# Panda · Servicio de IA (`ia-service/`)

**Responsable:** Estefanía López Rivas · **Estado:** cierre del Sprint 6 (2026-11-27)

Servicio FastAPI que sirve el modelo de visión entrenado en `comida.ipynb` y el cálculo de minutos de actividad.
Solo lo llama el backend de Panda: todas las rutas `/v1/*` piden `X-API-Key`. El servicio no guarda nada: ni
fotos, ni resultados, ni datos de usuarios.

| Ruta | Para qué | Historia |
|---|---|---|
| `GET /health` | El proceso está vivo (sin autenticación) | HU-75 · SCRUM-734 |
| `GET /ready` | 503 hasta que el modelo, las métricas y los compendios están cargados | HU-75 · SCRUM-734 |
| `POST /v1/vision/estimar` | Foto → calorías y macronutrientes, con rango ±%MAE y avisos | HU-83 · SCRUM-736 |
| `GET /v1/actividad/catalogo?edad=` | Actividades del compendio que corresponde a la edad | HU-85 · SCRUM-738 |
| `POST /v1/actividad/calcular` | Minutos de una actividad para gastar las kcal (fórmula neta o bruta) | HU-85 · SCRUM-738 |

La documentación interactiva está en `/docs` y el contrato de visión en [`docs/contrato-vision.md`](docs/contrato-vision.md).

## Arrancar en local

```bash
cd ia-service
python3.12 -m venv .venv && source .venv/bin/activate
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.15.0 torchvision==0.29.2
pip install -r requirements/dev.txt
cp .env.example .env            # IA_MODELO=falso para trabajar sin pesos
uvicorn app.main:create_app --factory --reload --port 8100
```

Con el modelo real, define en `.env`:

```dotenv
IA_MODELO=siglip
IA_MODELO_URL=https://github.com/Ludwig-Ivan/Panda/releases/download/modelo-v1/best.pt
IA_MODELO_SHA256=<el que imprime scripts/publicar_modelo.py>
IA_MODELO_DIR=./.modelos
```

En desarrollo también sirve `IA_MODELO_URL=file:///ruta/a/best.pt`.

### Página de prueba

Con el servicio corriendo abre http://localhost:8100/demo: subes la foto, ves los nutrientes con su rango, ajustas
calorías, peso y edad, y eliges categoría y actividad (igual que las secciones 10-12 del notebook). Solo para
desarrollo; en producción `IA_DEMO=false`.

### Conectar el modelo real (best.pt)

Con uvicorn apagado: `python scripts/conectar_modelo.py` descarga `best.pt` desde Drive (o `--url` de Hugging Face / GitHub Release), lo deja en la caché, calcula el SHA-256 y actualiza el `.env`. Después arranca uvicorn normal.

### Prueba rápida en la terminal

Con el servicio corriendo, abre otra terminal (con el venv activado) y ejecuta:

```bash
python scripts/probar.py ruta/a/una/foto.jpg
python scripts/probar.py foto.jpg --peso 60 --edad 22 --actividad 1202860
```

Muestra el estado del servicio, los nutrientes estimados con su rango, el tiempo de actividad y otras opciones del catálogo.

## Docker

```bash
cp .env.example .env
docker compose --profile cpu up ia          # CPU
docker compose --profile gpu up ia-gpu      # GPU (necesita NVIDIA Container Toolkit)
```

En los dos perfiles el servicio es accesible como `ia` dentro de la red de compose, y en el puerto `8100` del host.
`best.pt` se guarda en el volumen `modelos`: se descarga una sola vez y en cada arranque se verifica de nuevo su
SHA-256.

## Pruebas

```bash
ruff check . && ruff format --check .
pytest -q                                  # sin red, sin GPU y sin pesos (modelo falso y un SigLIP diminuto)
IA_MODELO_PATH=/ruta/best.pt pytest -m regresion -s   # T-214: 10 fotos fijas contra el notebook (±1 %)
```

La CI (`.github/workflows/ia-ci.yml`) corre lint y pruebas, y construye la imagen CPU.

## Estructura

```
ia-service/
├── app/
│   ├── main.py             create_app() y lifespan: carga en segundo plano
│   ├── config.py           variables IA_*
│   ├── seguridad.py        X-API-Key (varias claves, para poder rotarlas)
│   ├── limite.py           413 antes de leer cuerpos de más de 10 MB
│   ├── estado.py           estado de carga que consulta /ready
│   ├── vision/             modelo (port del notebook), preprocesamiento, validación de la imagen,
│   │                       pesos con SHA-256, rango ±%MAE, endpoint
│   └── actividad/          compendios 2024, fórmula neta o bruta, endpoints
├── data/                   compendios exportados del notebook (T-220)
├── modelo/                 test_metrics.json real y ficha del modelo (T-209)
├── scripts/                exportar_compendios.py, publicar_modelo.py
├── docs/contrato-vision.md propuesta para SCRUM-768
└── tests/
```

## Pendientes que no se pueden cerrar desde el código

| Pendiente | Qué falta | Historia |
|---|---|---|
| Publicar `best.pt` | Descargarlo de Drive (`MyDrive/n5k_runs/caloriek_ft/`), correr `scripts/publicar_modelo.py` y crear el release `modelo-v1` | T-209 |
| Regresión con 10 fotos | Elegir las fotos y generar `esperado.json` desde el notebook (`tests/regresion/fotos/README.md`) | T-214 |
| Contrato de visión | Acordar con Iván la opción A o B y actualizar AD-06 | SCRUM-768 |
| Quién calcula la fórmula | HU-85 pide acordar con Iván si los minutos salen de aquí o de SCRUM-445 en el backend | HU-85 |
