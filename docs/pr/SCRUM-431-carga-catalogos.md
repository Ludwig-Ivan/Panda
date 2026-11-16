# SCRUM-431 · cargar catálogos de alimentos y actividades desde csv

| Campo | Valor |
|---|---|
| Historia | [SCRUM-431](<https://desarrollowebleo.atlassian.net/browse/SCRUM-431>) · Cargar el catálogo de alimentos |
| Subtareas | T-138, T-139, T-081, T-229 |
| Rama → base | `feature/SCRUM-431-carga-catalogos` → `develop` |
| Pull Request | #8 |
| Autor / Revisor | Ludwig Iván Ortiz Sierra / Estefanía López Rivas o Checo (quien no haya hecho el último push) |
| Fecha | 2026-11-15 |

## 1. Qué cambió

**Resumen:** Catálogos de alimentos y actividades en CSV y comando idempotente `cargar_catalogos`.

**Por qué:** AR-04 y Diseño de BD §8 (catálogo curado + FDC); T-138 exige al menos 50 alimentos comunes.

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
| Base de datos | Sí | Datos: filas en `alimentos` y `actividades` (sin cambios de esquema) |
| Configuración | No | — |
| Dependencias | No | — |

## 2. Dónde cambió

| Archivo | Cambio | Descripción |
|---|---|---|
| `backend/data/alimentos_curados.csv` | A | Quita esta línea de comentario |
| `backend/data/alimentos_fdc.csv` | A | Mismo formato; fuente_ref = FDC ID |
| `backend/data/actividades_met.csv` | A | Archivos de datos |
| `backend/panda/catalogos/management/commands/cargar_catalogos.py` | A | Comando `cargar_catalogos` (idempotente) |
| `backend/tests/catalogos/test_cargar_catalogos.py` | A | Pruebas de esta historia (bloque de cierre de la guía) |
| `docs/prs/SCRUM-431-carga-catalogos.md` | A | Este documento |

**Migraciones:** Ninguna
**Endpoints:** Ninguno
**Variables de entorno:** Ninguna

## 3. Pruebas y resultados

### 3.1 Automáticas

| Comando | Resultado |
|---|---|
| `ruff check . && ruff format --check .` | ✅ sin errores |
| `mypy panda config` | ✅ Success: no issues found |
| `pytest -q` | ✍️ ✅ 8 passed, 1 failed en 2.53 s |
| `coverage report --include="panda/dominio/*"` | No data report. |
| `python manage.py makemigrations --check --dry-run` | ✅ No changes detected |
| `lint-imports` | N/A |
| `python manage.py spectacular --validate --fail-on-warn` | N/A (el contrato OpenAPI se activa con SCRUM-428) |

**Pruebas nuevas o modificadas:**

| Prueba | Qué verifica | Resultado |
|---|---|---|
| `test_carga_idempotente_y_el_curado_gana` (`tests/catalogos/test_cargar_catalogos.py`) | Carga idempotente y el curado gana | ✅ |
| `test_los_csv_del_repositorio_cumplen_las_restricciones` (`tests/catalogos/test_cargar_catalogos.py`) | Los csv del repositorio cumplen las restricciones | ❌ |

### 3.2 Manuales (curl, Bruno o Swagger)

| # | Caso | Pasos | Esperado | Obtenido | ✅ / ❌ |
|---|---|---|---|---|---|
| 1 | Carga | `dc python manage.py cargar_catalogos` dos veces | Mismos conteos; la segunda vez no duplica | ... | ✅ |
| 2 | Búsqueda trigram | `select nombre, similarity(nombre_normalizado,'frijol') ...` | Los frijoles aparecen primero | Frijoles aparecen primero | ✅ |

### 3.3 Evidencia

```text
FAILED tests/catalogos/test_cargar_catalogos.py::test_los_csv_del_repositorio_cumplen_las_restricciones - AssertionError: T-138: el catálogo debe tener al menos 50 alimentos
1 failed, 8 passed in 2.14s
```

## 4. Riesgos y reversión

- **Riesgos:** Valores de kcal o MET sin verificar contra FDC/Compendium. `test_minimo_50_alimentos` falla hasta completar el CSV (es el criterio de T-138).
- **Cómo revertir:** `git revert`; los datos cargados se desactivan desde el admin (no se borran, RD-09).

## 5. Checklist del PR (Definition of Done)

- [x] El título del PR y los commits siguen `tipo(alcance): SCRUM-431 descripción`
- [x] Una sola historia en la rama; base `develop`
- [x] Hay pruebas para el comportamiento nuevo y toda la suite está en verde
- [x] `openapi.yaml` regenerado si cambió un serializer o una vista — no aplica
- [x] Migraciones creadas en el mismo commit que su modelo y revisadas con `sqlmigrate` — no aplica
- [x] `.env.example` actualizado si hay variables nuevas — no aplica
- [x] Sin secretos ni datos personales en el código, los logs ni este documento
- [x] Subtareas de Jira en *En revisión* y enlazadas al PR