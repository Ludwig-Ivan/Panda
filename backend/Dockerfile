FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
RUN useradd --create-home --uid 1000 panda

ARG REQUIREMENTS=base
COPY requirements/ requirements/
RUN pip install -r requirements/${REQUIREMENTS}.txt

COPY . .

# Estáticos del admin (WhiteNoise). Variables ficticias solo para el build.
RUN DJANGO_SETTINGS_MODULE=config.settings.prod \
    DJANGO_SECRET_KEY=solo-para-build \
    DATABASE_URL=sqlite:////tmp/build.db \
    STORAGE_BACKEND=memory \
    python manage.py collectstatic --noinput

USER panda
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT} --workers 3 --worker-class gthread --threads 4 --timeout 30 --access-logfile -"]