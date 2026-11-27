# ia-service/Dockerfile  (T-205)
# Dos variantes con el mismo código y las mismas versiones (probadas: torch 2.15.0 + transformers 5.24.1):
#   docker build --build-arg VARIANTE=cpu -t panda-ia:cpu .   → torch CPU (~1 GB)
#   docker build --build-arg VARIANTE=gpu -t panda-ia:gpu .   → torch de PyPI, que trae CUDA en el wheel (~5 GB)
# La variante GPU solo necesita el driver de NVIDIA en el host y NVIDIA Container Toolkit; no hace falta una imagen base
# de CUDA. transformers 5.x exige torch >= 2.6.
ARG VARIANTE=cpu

FROM python:3.12-slim AS base-cpu
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu "torch==2.15.0" "torchvision==0.29.2"

FROM python:3.12-slim AS base-gpu
RUN pip install --no-cache-dir "torch==2.15.0" "torchvision==0.29.2"

FROM base-${VARIANTE} AS final
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    IA_MODELO_DIR=/modelos

WORKDIR /app
RUN useradd --create-home --uid 1000 ia && mkdir -p /modelos && chown ia /modelos

COPY requirements/ requirements/
RUN pip install -r requirements/vision.txt

COPY app/ app/
COPY data/ data/
COPY modelo/ modelo/

USER ia
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"
# Un solo worker: cada worker cargaría su propia copia del modelo (~1.5 GB de RAM o VRAM)
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
