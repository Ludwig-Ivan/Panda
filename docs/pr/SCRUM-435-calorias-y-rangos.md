# SCRUM-435 · cálculo de kcal por porción y rangos en el dominio

| Campo | Valor |
|---|---|
| Historia | [SCRUM-435](<https://desarrollowebleo.atlassian.net/browse/SCRUM-435>) · Calcular las calorías con un rango |
| Subtareas | T-059, T-060, T-230 |
| Rama → base | `feature/SCRUM-435-calorias-y-rangos` → `develop` |
| Pull Request | #10 |
| Autor / Revisor | Ludwig Iván Ortiz Sierra |
| Fecha | 2026-11-16 |

## 1. Qué cambió

**Resumen:** Cálculo puro de kcal por porción, factor de rango según confianza y fuente, y totales redondeados a la decena.

**Por qué:** RF-03 a RF-05, RNF-CF-04 y RNF-RU-01 (dominio sin frameworks); Architecture C-04 pasos 4–6.

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
| `backend/panda/dominio/calorias.py` | A | Calorías y rangos |
| `backend/tests/dominio/test_calorias.py` | A | Pruebas del Paso 17.4 que cubren esta historia |
| `docs/prs/SCRUM-435-calorias-y-rangos.md` | A | Este documento |

**Migraciones:** Ninguna
**Endpoints:** Ninguno
**Variables de entorno:** Ninguna

## 3. Pruebas y resultados

### 3.1 Automáticas

| Comando | Resultado |
|---|---|
| `ruff check . && ruff format --check .` | ✅ sin errores |
| `mypy panda config` | ✅ Success: no issues found |
| `pytest -q` | ✅ 25 passed, 2 failed en 15.31 s |
| `coverage report --include="panda/dominio/*"` | No data report |
| `python manage.py makemigrations --check --dry-run` | No changes detected |
| `lint-imports` | N/A |
| `python manage.py spectacular --validate --fail-on-warn` | N/A (el contrato OpenAPI se activa con SCRUM-428) |

**Pruebas nuevas o modificadas:**

| Prueba | Qué verifica | Resultado |
|---|---|---|
| `test_ejemplo_de_la_api` (`tests/dominio/test_calorias.py`) | Ejemplo de la API | ✅ |
| `test_usuario_usa_factor_fijo` (`tests/dominio/test_calorias.py`) | Usuario usa factor fijo | ✅ |
| `test_estimado_ia_amplia_el_rango_y_pide_revision` (`tests/dominio/test_calorias.py`) | Estimado ia amplia el rango y pide revision | ✅ |
| `test_redondeo_half_up` (`tests/dominio/test_calorias.py`) | Redondeo half up | ✅ |
| `test_entradas_invalidas` (`tests/dominio/test_calorias.py`) | Entradas inválidas | ✅ |
| `test_el_rango_siempre_contiene_el_valor` (`tests/dominio/test_calorias.py`) | El rango siempre contiene el valor | ✅ |
| `test_total_dentro_del_rango` (`tests/dominio/test_calorias.py`) | Total dentro del rango | ✅ |

### 3.2 Manuales (curl, Bruno o Swagger)

| # | Caso | Pasos | Esperado | Obtenido | ✅ / ❌ |
|---|---|---|---|---|---|
| 1 | Ejemplo de la API | `calcular_item` de tacos 180 g y frijoles 150 g | 316 [253, 379] y 134 [92, 176]; total 450 [350, 560] | Concuerda con el esperado | ✅ |

### 3.3 Evidencia

```text
FAILED tests/catalogos/test_cargar_catalogos.py::test_los_csv_del_repositorio_cumplen_las_restricciones - AssertionError: T-138: el catálogo debe tener al menos 50 alimentos
1 failed, 26 passed, 1 warning in 15.74s
```

## 4. Riesgos y reversión

- **Riesgos:** Ninguno en tiempo de ejecución: el módulo aún no se usa desde la API.
- **Cómo revertir:** `git revert` del squash.

## 5. Checklist del PR (Definition of Done)

- [X] El título del PR y los commits siguen `tipo(alcance): SCRUM-435 descripción`
- [X] Una sola historia en la rama; base `develop`
- [X] Hay pruebas para el comportamiento nuevo y toda la suite está en verde
- [x] `openapi.yaml` regenerado si cambió un serializer o una vista — no aplica
- [x] Migraciones creadas en el mismo commit que su modelo y revisadas con `sqlmigrate` — no aplica
- [x] `.env.example` actualizado si hay variables nuevas — no aplica
- [X] Sin secretos ni datos personales en el código, los logs ni este documento
- [X] Subtareas de Jira en *En revisión* y enlazadas al PR