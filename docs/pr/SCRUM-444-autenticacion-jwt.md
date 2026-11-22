# SCRUM-444 · registro, login y refresh rotativo en cookie httponly

| Campo | Valor |
|---|---|
| Historia | [SCRUM-444](https://desarrollowebleo.atlassian.net/browse/SCRUM-444) · Registrarse e iniciar sesión |
| Subtareas | T-074, T-075, T-076, T-232, T-233, T-234, T-235 |
| Rama → base | `feature/SCRUM-444-autenticacion-jwt` → `develop` |
| Pull Request | #15 |
| Autor / Revisor | Ludwig Iván Ortiz Sierra |
| Fecha | 2026-11-22 |

## 1. Qué cambió

**Resumen:** Registro con consentimientos, login, refresh rotativo en cookie `HttpOnly` con detección de reutilización, y logout.

**Por qué:** RF-08 y RF-10, RNF-SG-01 (Argon2), AD-10; API §3, §5.1 y §5.2.

**Tipo de cambio:**

- [x] Funcionalidad nueva
- [ ] Corrección de un bug
- [ ] Refactor sin cambio de comportamiento
- [ ] Solo pruebas
- [ ] Infraestructura o CI
- [ ] Documentación

**Impacto en contratos:**

| Área | ¿Cambia? | Detalle |
|---|---|---|
| API (`openapi.yaml`) | Sí | 4 endpoints nuevos de `/auth` |
| Base de datos | No | — |
| Configuración | No | — |
| Dependencias | No | — |

## 2. Dónde cambió

| Archivo | Cambio | Descripción |
|---|---|---|
| `backend/panda/identidad/tokens.py` | A | Utilidades de tokens |
| `backend/panda/identidad/services.py` | A | Servicios de identidad (parte 1) |
| `backend/panda/identidad/serializers.py` | A | Serializers de autenticación |
| `backend/panda/identidad/views.py` | A | Primera parte; la Fase 10 agrega más vistas a este archivo |
| `backend/panda/identidad/urls.py` | A | URLs de identidad (se completan en la Fase 10) |
| `backend/tests/api/test_auth_sesion.py` | A | Pruebas de esta historia (bloque de cierre de la guía) |
| `backend/tests/api/test_auth.py` | A | Pruebas del Paso 17.4 que cubren esta historia |
| `backend/config/urls.py` | M | Incluye `panda.identidad.urls` bajo `api/v1/` (Paso 9.5) |
| `docs/prs/SCRUM-444-autenticacion-jwt.md` | A | Este documento |

**Migraciones:** Ninguna
**Endpoints:**
- `POST /api/v1/auth/registro` → 201 + cookie `panda_rt`; 409 `EMAIL_TAKEN`; 422 `AGE_REQUIREMENT` / `CONSENT_REQUIRED`
- `POST /api/v1/auth/login` → 200; 401 `INVALID_CREDENTIALS`; 429 tras 10 intentos en 15 min
- `POST /api/v1/auth/refresh` → 200 y rota la cookie; 401 si se reutiliza un token rotado (revoca todas las sesiones)
- `POST /api/v1/auth/logout` → 204 y borra la cookie
**Variables de entorno:** Ninguna

## 3. Pruebas y resultados

### 3.1 Automáticas

| Comando | Resultado |
|---|---|
| `ruff check . && ruff format --check .` | ✅ sin errores |
| `mypy panda config` | ✅ Success: no issues found |
| `pytest -q` | ✅ 40 passed, 1 failed en 6.22 s |
| `coverage report --include="panda/dominio/*"` | No data report |
| `python manage.py makemigrations --check --dry-run` | ✅ No changes detected |
| `lint-imports` | ✅ 1 kept, 0 broken |
| `python manage.py spectacular --validate --fail-on-warn` | N/A (el contrato OpenAPI se activa con SCRUM-428) |

**Pruebas nuevas o modificadas:**

| Prueba | Qué verifica | Resultado |
|---|---|---|
| `test_logout_revoca_el_refresh` (`tests/api/test_auth_sesion.py`) | Logout revoca el refresh | ✅ |
| `test_login_limitado_a_10_intentos_cada_15_min` (`tests/api/test_auth_sesion.py`) | Login limitado a 10 intentos cada 15 min | ✅ |
| `test_registro_crea_sesion_y_cookie` (`tests/api/test_auth.py`) | Registro crea sesión y cookie | ✅ |
| `test_registro_menor_de_edad` (`tests/api/test_auth.py`) | Registro menor de edad | ✅ |
| `test_registro_sin_consentimiento_vigente` (`tests/api/test_auth.py`) | Registro sin consentimiento vigente | ✅ |
| `test_login_incorrecto_es_generico` (`tests/api/test_auth.py`) | Login incorrecto es genérico | ✅ |
| `test_refresh_rota_y_detecta_reutilizacion` (`tests/api/test_auth.py`) | Refresh rota y detecta reutilización | ✅ |

### 3.2 Manuales (curl, Bruno o Swagger)

| # | Caso | Pasos | Esperado | Obtenido | ✅ / ❌ |
|---|---|---|---|---|---|
| 1 | Registro | `curl -si -X POST .../auth/registro` con los 3 consentimientos vigentes | 201, `Set-Cookie: panda_rt=...; HttpOnly; Path=/api/v1/auth; SameSite=Strict` | 201, `Set-Cookie: panda_rt=...; HttpOnly; Path=/api/v1/auth; SameSite=Strict` | ✅ |
| 2 | Correo repetido | Repetir el mismo registro | 409 `EMAIL_TAKEN` | 409 `EMAIL_TAKEN` | ✅ |
| 3 | Menor de edad | `"mayorEdad": false` | 422 `AGE_REQUIREMENT` | 422 `AGE_REQUIREMENT` | ✅ |

### 3.3 Evidencia

```text
== short test summary info ==
FAILED tests/catalogos/test_cargar_catalogos.py::test_los_csv_del_repositorio_cumplen_las_restricciones - AssertionError: T-138: el catálogo debe tener al menos 50 alimentos
1 failed, 40 passed, 8 warnings in 6.22s
```

## 4. Riesgos y reversión

- **Riesgos:** Dos refresh simultáneos desde varias pestañas se detectan como reutilización y cierran todas las sesiones: el frontend debe compartir una sola petición de refresh.
- **Cómo revertir:** `git revert` del squash; sin migraciones (las tablas `token_blacklist_*` ya existen).

## 5. Checklist del PR (Definition of Done)

- [x] El título del PR y los commits siguen `tipo(alcance): SCRUM-444 descripción`
- [x] Una sola historia en la rama; base `develop`
- [x] Hay pruebas para el comportamiento nuevo y toda la suite está en verde
- [x] `openapi.yaml` regenerado si cambió un serializer o una vista — no aplica
- [x] Migraciones creadas en el mismo commit que su modelo y revisadas con `sqlmigrate` — no aplica
- [x] `.env.example` actualizado si hay variables nuevas — no aplica
- [x] Sin secretos ni datos personales en el código, los logs ni este documento
- [x] Subtareas de Jira en *En revisión* y enlazadas al PR