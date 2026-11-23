# SCRUM-633 · api de cuenta, perfil, consentimientos y preferencias

| Campo | Valor |
|---|---|
| Historia | [SCRUM-633](https://desarrollowebleo.atlassian.net/browse/SCRUM-633) · Exponer la API de cuenta, perfil, consentimientos y preferencias |
| Subtareas | T-185, T-186, T-187, T-188 |
| Rama → base | `feature/SCRUM-633-api-cuenta-perfil` → `develop` |
| Pull Request | #17 |
| Autor / Revisor | Ludwig Iván Ortiz Sierra |
| Fecha | 2026-11-22 |

## 1. Qué cambió

**Resumen:** API de cuenta, perfil, consentimientos y preferencias de actividad, y el permiso que exige perfil y avisos vigentes.

**Por qué:** RF-09, RF-13, RD-01, RNF-CU-01 y RNF-CU-02.

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
| API (`openapi.yaml`) | Sí | 7 operaciones nuevas |
| Base de datos | No | — |
| Configuración | No | — |
| Dependencias | No | — |

## 2. Dónde cambió

| Archivo | Cambio | Descripción |
|---|---|---|
| `backend/panda/identidad/services.py` | M | Continuación |
| `backend/panda/identidad/permisos.py` | A | Permiso de precondiciones |
| `backend/panda/identidad/views.py` | M | Continuación |
| `backend/panda/identidad/urls.py` | M | Versión final |
| `backend/tests/api/test_cuenta.py` | A | Pruebas de esta historia (bloque de cierre de la guía) |
| `docs/prs/SCRUM-633-api-cuenta-perfil.md` | A | Este documento |

**Migraciones:** Ninguna
**Endpoints:**
- `GET /api/v1/usuarios/me` · `PATCH /api/v1/usuarios/me` (`guardarFotos`)
- `GET /api/v1/consentimientos` · `POST /api/v1/consentimientos` → 400 si la versión no es la vigente
- `GET /api/v1/perfil` (404 si no existe) · `PUT /api/v1/perfil` → 400 con `details` por campo
- `GET /api/v1/perfil/preferencias-actividad` · `PUT` → 404 si alguna actividad no existe
**Variables de entorno:** Ninguna

## 3. Pruebas y resultados

### 3.1 Automáticas

| Comando | Resultado |
|---|---|
| `ruff check . && ruff format --check .` | ✅ sin errores |
| `mypy panda config` | ✅ Success: no issues found |
| `pytest -q` | ✅ 45 passed, 1 failed en 4.59 s |
| `coverage report --include="panda/dominio/*"` | No data report |
| `python manage.py makemigrations --check --dry-run` | ✅ No changes detected |
| `lint-imports` | ✅ 1 kept, 0 broken |
| `python manage.py spectacular --validate --fail-on-warn` | N/A (el contrato OpenAPI se activa con SCRUM-428) |

**Pruebas nuevas o modificadas:**

| Prueba | Qué verifica | Resultado |
|---|---|---|
| `test_perfil_se_crea_y_actualiza` (`tests/api/test_cuenta.py`) | Perfil se crea y actualiza | ✅ |
| `test_perfil_fuera_de_rango` (`tests/api/test_cuenta.py`) | Perfil fuera de rango | ✅ |
| `test_solo_se_acepta_la_version_vigente_de_los_avisos` (`tests/api/test_cuenta.py`) | Solo se acepta la version vigente de los avisos | ✅ |
| `test_preferencias_sin_duplicados_y_validadas` (`tests/api/test_cuenta.py`) | Preferencias sin duplicados y validadas | ✅ |
| `test_desactivar_el_guardado_de_fotos` (`tests/api/test_cuenta.py`) | Desactivar el guardado de fotos | ✅ |

### 3.2 Manuales (curl, Bruno o Swagger)

| # | Caso | Pasos | Esperado | Obtenido | ✅ / ❌ |
|---|---|---|---|---|---|
| 1 | Perfil | `PUT /perfil` con edad 29, 62.5 kg, 163 cm | 200; `GET /usuarios/me` → `perfilCompleto: true` | 200; `GET /usuarios/me` → `perfilCompleto: true` | ✅ |
| 2 | Edad inválida | `PUT /perfil` con `edad: 15` | 400 `VALIDATION_ERROR`, `details[0].field = "edad"` | 400 `VALIDATION_ERROR`, `details[0].field = "edad"` | ✅ |

### 3.3 Evidencia

```text
== short test summary info ==
FAILED tests/catalogos/test_cargar_catalogos.py::test_los_csv_del_repositorio_cumplen_las_restricciones - AssertionError: T-138: el catálogo debe tener al menos 50 alimentos
1 failed, 45 passed, 13 warnings in 4.59s
```

## 4. Riesgos y reversión

- **Riesgos:** El permiso `TienePerfilYConsentimientos` no debe aplicarse a consultas, exportación ni borrado (RNF-CU-02).
- **Cómo revertir:** `git revert` del squash; sin migraciones.

## 5. Checklist del PR (Definition of Done)

- [x] El título del PR y los commits siguen `tipo(alcance): SCRUM-633 descripción`
- [x] Una sola historia en la rama; base `develop`
- [x] Hay pruebas para el comportamiento nuevo y toda la suite está en verde
- [x] `openapi.yaml` regenerado si cambió un serializer o una vista — no aplica
- [x] Migraciones creadas en el mismo commit que su modelo y revisadas con `sqlmigrate` — no aplica
- [x] `.env.example` actualizado si hay variables nuevas — no aplica
- [x] Sin secretos ni datos personales en el código, los logs ni este documento
- [x] Subtareas de Jira en *En revisión* y enlazadas al PR