# SCRUM-427 · workflow backend-ci con lint, tipos, capas, migraciones y pruebas

| Campo | Valor |
|---|---|
| Historia | [SCRUM-427](https://desarrollowebleo.atlassian.net/browse/SCRUM-427) · Preparar el repositorio y los entornos (CI del backend) |
| Subtareas | T-044, T-226, T-227, T-228 |
| Rama → base | `ci/SCRUM-427-backend-ci` → `develop` |
| Pull Request | #14 |
| Autor / Revisor | Ludwig Iván Ortiz Sierra |
| Fecha | 2026-11-21 |

## 1. Qué cambió

**Resumen:** Pipeline `backend-ci` con lint, tipos, contrato de capas, migraciones al día, pruebas, `check --deploy`, `pip-audit` y gitleaks.

**Por qué:** RNF-MA-03 (calidad verificable), RNF-SG-07 (sin secretos en el repo); Fase 18 y CR-06 de la Guía de Configuración.

**Tipo de cambio:**

- [ ] Funcionalidad nueva
- [ ] Corrección de un bug
- [ ] Refactor sin cambio de comportamiento
- [ ] Solo pruebas
- [x] Infraestructura o CI
- [ ] Documentación

**Impacto en contratos:**

| Área | ¿Cambia? | Detalle |
|---|---|---|
| API (`openapi.yaml`) | No | — |
| Base de datos | No | — |
| Configuración | No | — |
| Dependencias | No | — |

> Se sube **sin** el paso «Contrato OpenAPI» (llega con SCRUM-428) y **sin**`--fail-under=80` (llega con SCRUM-642).

## 2. Dónde cambió

| Archivo | Cambio | Descripción |
|---|---|---|
| `backend/pyproject.toml` | M | Configuración |
| `backend/.importlinter` | A | Contrato de capas con import-linter |
| `.pre-commit-config.yaml` | A | En la raíz del repo |
| `.github/workflows/backend-ci.yml` | A | En la raíz del repo |
| `docs/prs/SCRUM-427-backend-ci.md` | A | Este documento |

**Migraciones:** Ninguna
**Endpoints:** Ninguno
**Variables de entorno:** Ninguna

## 3. Pruebas y resultados

### 3.1 Automáticas

| Comando | Resultado |
|---|---|
| `ruff check . && ruff format --check .` | ✅ sin errores |
| `mypy panda config` | ✅ Success: no issues found |
| `pytest -q` | ✅ 33 passed, 1 failed en 6.29 s |
| `coverage report --include="panda/dominio/*"` | No data found. |
| `python manage.py makemigrations --check --dry-run` | ✅ No changes detected |
| `lint-imports` | ✅ 1 kept, 0 broken |
| `python manage.py spectacular --validate --fail-on-warn` | N/A (el contrato OpenAPI se activa con SCRUM-428) |

**Pruebas nuevas o modificadas:**

| Prueba | Qué verifica | Resultado |
|---|---|---|
| — | Esta historia no agrega pruebas automáticas; se verifica con los casos manuales de 3.2 | — |

### 3.2 Manuales (curl, Bruno o Swagger)

| # | Caso | Pasos | Esperado | Obtenido | ✅ / ❌ |
|---|---|---|---|---|---|
| 1 | CI completa | Abrir el PR | `calidad-y-pruebas` y `secretos` en verde | en verde | ✅ |
| 2 | Prueba negativa | En una rama temporal, cambiar un modelo sin migración | «Migraciones al día» ❌ | «Migraciones al día» ❌ | ✅ |

### 3.3 Evidencia

```text
== short test summary info ==
FAILED tests/catalogos/test_cargar_catalogos.py::test_los_csv_del_repositorio_cumplen_las_restricciones - AssertionError: T-138: el catálogo debe tener al menos 50 alimentos
1 failed, 33 passed, 1 warning in 6.29s
```

## 4. Riesgos y reversión

- **Riesgos:** Al marcar `calidad-y-pruebas` como obligatorio, cualquier PR que lo rompa queda bloqueado: activarlo en el ruleset solo después de verlo en verde.
- **Cómo revertir:** `git revert` del squash y quitar el check del ruleset.

## 5. Checklist del PR (Definition of Done)

- [x] El título del PR y los commits siguen `tipo(alcance): SCRUM-427 descripción`
- [x] Una sola historia en la rama; base `develop`
- [x] Hay pruebas para el comportamiento nuevo y toda la suite está en verde
- [x] `openapi.yaml` regenerado si cambió un serializer o una vista — no aplica
- [x] Migraciones creadas en el mismo commit que su modelo y revisadas con `sqlmigrate` — no aplica
- [x] `.env.example` actualizado si hay variables nuevas — no aplica
- [x] Sin secretos ni datos personales en el código, los logs ni este documento
- [x] Subtareas de Jira en *En revisión* y enlazadas al PR