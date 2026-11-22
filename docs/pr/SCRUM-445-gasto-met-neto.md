# SCRUM-445 · gasto energético con met neto (met-neto-v1)

| Campo | Valor |
|---|---|
| Historia | [SCRUM-445](https://desarrollowebleo.atlassian.net/browse/SCRUM-445) · Calcular el gasto de cada actividad |
| Subtareas | T-080, T-082 |
| Rama → base | `feature/SCRUM-445-gasto-met-neto` → `develop` |
| Pull Request | #12 |
| Autor / Revisor | Ludwig Iván Ortiz Sierra |
| Fecha | 2026-11-21 |

## 1. Qué cambió

**Resumen:** Fórmula `met-neto-v1`: kcal/min = (MET − 1) × 3.5 × peso / 200, con enumeraciones de intensidad y nivel.

**Por qué:** RF-11 y AD-08 (MET neto); caso del Apéndice A del SRS.

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
| API (`openapi.yaml`) | No | — |
| Base de datos | No | — |
| Configuración | No | — |
| Dependencias | No | — |

## 2. Dónde cambió

| Archivo | Cambio | Descripción |
|---|---|---|
| `backend/panda/dominio/recomendacion.py` | A | Gasto energético y recomendación |
| `backend/tests/dominio/test_recomendacion.py` | A | Pruebas del Paso 17.4 que cubren esta historia |
| `docs/prs/SCRUM-445-gasto-met-neto.md` | A | Este documento |

**Migraciones:** Ninguna
**Endpoints:** Ninguno
**Variables de entorno:** Ninguna

## 3. Pruebas y resultados

### 3.1 Automáticas

| Comando | Resultado |
|---|---|
| `ruff check . && ruff format --check .` | ✅ sin errores |
| `mypy panda config` | ✅ Success: no issues found |
| `pytest -q` | ✅ 26 passed, 1 failed en 20.01 s |
| `coverage report --include="panda/dominio/*"` | No data to report. |
| `python manage.py makemigrations --check --dry-run` | ✅ No changes detected |
| `lint-imports` | N/A |
| `python manage.py spectacular --validate --fail-on-warn` | N/A (el contrato OpenAPI se activa con SCRUM-428) |

**Pruebas nuevas o modificadas:**

| Prueba | Qué verifica | Resultado |
|---|---|---|
| `test_formula_met_neto` (`tests/dominio/test_recomendacion.py`) | Fórmula MET neto | ✅ |

### 3.2 Manuales (curl, Bruno o Swagger)

| # | Caso | Pasos | Esperado | Obtenido | ✅ / ❌ |
|---|---|---|---|---|---|
| 1 | Fórmula | `kcal_por_minuto(6.8, 70)` | 7.105 | 7.105 | ✅ |

### 3.3 Evidencia

```text
== short test summary info ==
FAILED tests/catalogos/test_cargar_catalogos.py::test_los_csv_del_repositorio_cumplen_las_restricciones - AssertionError: T-138: el catálogo debe tener al menos 50 alimentos
1 failed, 26 passed, 1 warning in 20.01s
```

## 4. Riesgos y reversión

- **Riesgos:** Ninguno en tiempo de ejecución.
- **Cómo revertir:** `git revert` del squash.

## 5. Checklist del PR (Definition of Done)

- [ ] El título del PR y los commits siguen `tipo(alcance): SCRUM-445 descripción`
- [ ] Una sola historia en la rama; base `develop`
- [ ] Hay pruebas para el comportamiento nuevo y toda la suite está en verde
- [x] `openapi.yaml` regenerado si cambió un serializer o una vista — no aplica
- [x] Migraciones creadas en el mismo commit que su modelo y revisadas con `sqlmigrate` — no aplica
- [x] `.env.example` actualizado si hay variables nuevas — no aplica
- [ ] Sin secretos ni datos personales en el código, los logs ni este documento
- [ ] Subtareas de Jira en *En revisión* y enlazadas al PR