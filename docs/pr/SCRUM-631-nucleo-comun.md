# SCRUM-631 · núcleo común de errores, request id, throttles e idempotencia

| Campo | Valor |
|---|---|
| Historia | [SCRUM-631](<https://desarrollowebleo.atlassian.net/browse/SCRUM-631>) · Construir el núcleo común de la API |
| Subtareas | T-172, T-173, T-174, T-175, T-176, T-177, T-178 |
| Rama → base | `feature/SCRUM-631-nucleo-comun` → `develop` |
| Pull Request | #6 |
| Autor / Revisor | Ludwig Iván Ortiz Sierra / Estefanía López Rivas o Checo (quien no haya hecho el último push) |
| Fecha | 2026-11-15 |

## 1. Qué cambió

**Resumen:** Núcleo común de la API: errores con el formato §7, `X-Request-Id`, throttles, idempotencia, paginación por cursor, borrado de fotos al confirmar y `/health`.

**Por qué:** RF-20 y RI-U-06 (mensajes claros sin detalles técnicos), RNF-SG-06 (límites de tasa), RNF-SG-11 (logs sin datos personales), API §7–§8.

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
| API (`openapi.yaml`) | Sí | `GET /health` (fuera de `/api/v1`); formato único de error `{error:{code,message,details,requestId}}` |
| Base de datos | No | — |
| Configuración | No | — |
| Dependencias | No | — |

## 2. Dónde cambió

| Archivo | Cambio | Descripción |
|---|---|---|
| `backend/panda/comun/errores.py` | A | Excepciones de negocio y manejador único de errores (API Specification §7). |
| `backend/panda/comun/middleware.py` | A | Middleware de `X-Request-Id` y log de acceso |
| `backend/panda/comun/throttles.py` | A | Límites de tasa |
| `backend/panda/comun/idempotencia.py` | A | Header Idempotency-Key en POST /estimaciones y POST /comidas (API §8). |
| `backend/panda/comun/paginacion.py` | A | Paginación por cursor con el formato de la API |
| `backend/panda/comun/almacenamiento.py` | A | Borrado de fotos después del commit |
| `backend/panda/comun/salud.py` | A | `/health` y respuestas JSON para 404/500 de Django |
| `backend/panda/comun/vistas.py` | A | `/health` y respuestas JSON para 404/500 de Django |
| `backend/tests/comun/test_errores.py` | A | Pruebas de esta historia (bloque de cierre de la guía) |
| `backend/tests/comun/test_middleware_y_utilidades.py` | A | Pruebas de esta historia (bloque de cierre de la guía) |
| `docs/prs/SCRUM-631-nucleo-comun.md` | A | Este documento |

**Migraciones:** Ninguna
**Endpoints:**
- `GET /health` → 200 `{status:"ok",version,checks}` o 503 si la BD no responde
**Variables de entorno:** Ninguna

## 3. Pruebas y resultados

### 3.1 Automáticas

| Comando | Resultado |
|---|---|
| `ruff check . && ruff format --check .` | ✅ sin errores |
| `mypy panda config` | ✅ Success: no issues found |
| `pytest -q` |  ✅ 7 passed, 0 failed en 1.25 s |
| `coverage report --include="panda/dominio/*"` | No data to report |
| `python manage.py makemigrations --check --dry-run` | ✅ No changes detected |
| `lint-imports` | N/A |
| `python manage.py spectacular --validate --fail-on-warn` | N/A (el contrato OpenAPI se activa con SCRUM-428) |

**Pruebas nuevas o modificadas:**

| Prueba | Qué verifica | Resultado |
|---|---|---|
| `test_error_de_negocio_con_formato_de_la_api` (`tests/comun/test_errores.py`) | Error de negocio con formato de la API | ✅ |
| `test_validacion_se_aplana_en_camel_case` (`tests/comun/test_errores.py`) | Validacion se aplana en camel case | ✅ |
| `test_error_no_controlado_no_expone_detalles` (`tests/comun/test_errores.py`) | Error no controlado no expone detalles | ✅ |
| `test_respeta_un_request_id_valido` (`tests/comun/test_middleware_y_utilidades.py`) | Respeta un request id válido | ✅ |
| `test_reemplaza_un_request_id_invalido` (`tests/comun/test_middleware_y_utilidades.py`) | Reemplaza un request id inválido | ✅ |
| `test_tasa_con_ventana_en_segundos` (`tests/comun/test_middleware_y_utilidades.py`) | Tasa con ventana en segundos | ✅ |
| `test_cursor_opaco_extrae_solo_el_token` (`tests/comun/test_middleware_y_utilidades.py`) | Cursor opaco extrae solo el token | ✅ |

### 3.2 Manuales (curl, Bruno o Swagger)

| # | Caso | Pasos | Esperado | Obtenido | ✅ / ❌ |
|---|---|---|---|---|---|
| 1 | Health | `curl -s localhost:8000/health` | 200 con `database: ok` | 200, `database: ok` | ✅ |
| 2 | Request id | `curl -si localhost:8000/health -H 'X-Request-Id: abc-123'` | La respuesta trae `X-Request-Id: abc-123` | La respuesta trae `X-Request-Id: abc-123` | ✅ |

### 3.3 Evidencia

```text
$ pytest tests/comun -q
....... [100%]
7 passed in 0.88s
```

## 4. Riesgos y reversión

- **Riesgos:** Si `NUM_PROXIES` no coincide con la plataforma, el throttle por IP puede falsearse (nota del Paso 4.3).
- **Cómo revertir:** `git revert` del squash; sin migraciones.

## 5. Checklist del PR (Definition of Done)

- [x] El título del PR y los commits siguen `tipo(alcance): SCRUM-631 descripción`
- [x] Una sola historia en la rama; base `backend`
- [x] Hay pruebas para el comportamiento nuevo y toda la suite está en verde
- [x] `openapi.yaml` regenerado si cambió un serializer o una vista — no aplica
- [x] Migraciones creadas en el mismo commit que su modelo y revisadas con `sqlmigrate` — no aplica
- [x] `.env.example` actualizado si hay variables nuevas — no aplica
- [x] Sin secretos ni datos personales en el código, los logs ni este documento
- [x] Subtareas de Jira en *En revisión* y enlazadas al PR