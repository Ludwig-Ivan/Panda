# SCRUM-630 · esqueleto del backend django con docker

| Campo | Valor |
|---|---|
| Historia | [SCRUM-630](https://desarrollowebleo.atlassian.net/browse/SCRUM-630) · Crear el esqueleto del backend Django con configuración por entorno |
| Subtareas | T-166, T-167, T-168, T-169, T-170, T-171 |
| Rama → base | `feature/SCRUM-630-esqueleto-backend` → `develop` |
| Pull Request | #5 |
| Autor / Revisor | Ludwig Iván Ortiz Sierra |
| Fecha | 2026-11-15 |

## 1. Qué cambió

**Resumen:** Proyecto Django 5.2 + DRF con apps de `panda`, settings por entorno (`base/dev/test/prod`) y Docker Compose con PostgreSQL 16.

**Por qué:** RNF-IN-02, RNF-IN-03 (arranque con un comando), RNF-SG-07 y RNF-MA-04 (configuración sensible fuera del código), API §5.1 (contraseña con letra y número).

**Tipo de cambio:**

- [x] Funcionalidad nueva
- [ ] Corrección de un bug
- [ ] Refactor sin cambio de comportamiento
- [ ] Solo pruebas
- [x] Infraestructura o CI
- [ ] Documentación

**Impacto en contratos:**

| Área | ¿Cambia? | Detalle |
|---|---|---|
| API (`openapi.yaml`) | No | — |
| Base de datos | Sí | PostgreSQL 16 en Docker Compose (aún sin migraciones propias) |
| Configuración | Sí | `.env.example` con todas las variables (`DJANGO_SECRET_KEY`, `DATABASE_URL`, `STORAGE_BACKEND`, `VISION_PROVIDER`, `ADMIN_URL`, …) |
| Dependencias | Sí | `requirements/base.txt` y `dev.txt` (Django 5.2, DRF 3.15, simplejwt, drf-spectacular, psycopg 3, argon2…) |

## 2. Dónde cambió

| Archivo | Cambio | Descripción |
|---|---|---|
| `backend/requirements/base.txt` | A | Entorno virtual y dependencias |
| `backend/requirements/dev.txt` | A | Entorno virtual y dependencias |
| `backend/manage.py` | A | Solo cambia esta línea |
| `backend/config/wsgi.py` | A | Solo cambia esta línea |
| `backend/panda/identidad/apps.py` | A | Repite en cada app con su nombre |
| `backend/.gitignore` | A | `.gitignore` y `.env.example` |
| `backend/.env.example` | A | Cópialo a .env y rellénalo; .env NUNCA se sube |
| `backend/config/settings/base.py` | A | `config/settings/base.py` |
| `backend/config/settings/dev.py` | A | Settings por entorno |
| `backend/config/settings/test.py` | A | Settings por entorno |
| `backend/config/settings/prod.py` | A | Staging y Producción; se distinguen con ENV |
| `backend/panda/identidad/validadores.py` | A | Validador de contraseña propio |
| `backend/Dockerfile` | A | `Dockerfile` |
| `backend/.dockerignore` | A | `Dockerfile` |
| `backend/docker-compose.yml` | A | `docker-compose.yml` |
| `backend/pyproject.toml` | A | Configuración de pytest, Ruff, mypy y coverage (T-171) |
| `backend/panda/{comun,identidad,catalogos,comidas,estimacion,recomendacion}/` | A | Apps creadas con `startapp` |
| `backend/config/asgi.py` | D | El MVP es WSGI (AD-11) |
| `docs/prs/SCRUM-630-esqueleto-backend.md` | A | Este documento |

**Migraciones:** Ninguna
**Endpoints:** Ninguno
**Variables de entorno:** Todas las de `.env.example`; en local se copia a `.env` (nunca se versiona).

## 3. Pruebas y resultados

### 3.1 Automáticas

| Comando | Resultado |
|---|---|
| `ruff check . && ruff format --check .` | ✅ sin errores |
| `mypy panda config` | ✅ Success: no issues found |
| `pytest -q` | ✅ <N> passed, 0 failed en <t> s |
| `python manage.py makemigrations --check --dry-run` | ✅ No changes detected |
| `python manage.py spectacular --validate --fail-on-warn` | N/A (el contrato OpenAPI se activa con SCRUM-428) |

**Pruebas nuevas o modificadas:**

| Prueba | Qué verifica | Resultado |
|---|---|---|
| — | Esta historia no agrega pruebas automáticas; se verifica con los casos manuales de 3.2 | — |

### 3.2 Manuales (curl, Bruno o Swagger)

| # | Caso | Pasos | Esperado | Obtenido | ✅ / ❌ |
|---|---|---|---|---|---|
| 1 | Lint | `ruff check . && ruff format --check .` | Sin errores | Sin errores | Y |
| 3 | PostgreSQL | `docker compose up -d db && docker compose ps` | `db` en estado *healthy* | health | Y |


## 4. Riesgos y reversión

- **Riesgos:** `AUTH_USER_MODEL` apunta a `identidad.Usuario`, que llega en SCRUM-632: no ejecutar `migrate` antes de ese PR.
- **Cómo revertir:** `git revert` del squash; no hay migraciones ni datos.

## 5. Checklist del PR (Definition of Done)

- [x] El título del PR y los commits siguen `tipo(alcance): SCRUM-630 descripción`
- [x] Una sola historia en la rama; base `develop`
- [x] Hay pruebas para el comportamiento nuevo y toda la suite está en verde
- [x] `openapi.yaml` regenerado si cambió un serializer o una vista — no aplica
- [x] Migraciones creadas en el mismo commit que su modelo y revisadas con `sqlmigrate` — no aplica
- [x] `.env.example` actualizado si hay variables nuevas
- [x] Sin secretos ni datos personales en el código, los logs ni este documento
- [x] Subtareas de Jira en *En revisión* y enlazadas al PR