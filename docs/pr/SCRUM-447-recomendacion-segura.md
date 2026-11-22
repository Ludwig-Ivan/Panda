# SCRUM-447 · recomendación con límites de duración y fraccionamiento

| Campo | Valor |
|---|---|
| Historia | [SCRUM-447](https://desarrollowebleo.atlassian.net/browse/SCRUM-447) · Recomendar actividades dentro de límites seguros |
| Subtareas | T-083, T-084, T-085, T-087, T-231 |
| Rama → base | `feature/SCRUM-447-recomendacion-segura` → `develop` |
| Pull Request | #13 |
| Autor / Revisor | Ludwig Iván Ortiz Sierra |
| Fecha | 2026-11-21 |

## 1. Qué cambió

**Resumen:** Recomendación segura: intensidades por nivel, preferidas primero, duración múltiplo de 5, fraccionamiento > 90 min y descarte > 180 min.

**Por qué:** RF-12, RF-14, RN-01 a RN-04, Architecture C-05.

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
| `backend/panda/dominio/recomendacion.py` | M | Gasto energético y recomendación |
| `backend/tests/dominio/test_recomendacion.py` | M | Pruebas del Paso 17.4 que cubren esta historia |
| `docs/prs/SCRUM-447-recomendacion-segura.md` | A | Este documento |

**Migraciones:** Ninguna
**Endpoints:** Ninguno
**Variables de entorno:** Ninguna

## 3. Pruebas y resultados

### 3.1 Automáticas

| Comando | Resultado |
|---|---|
| `ruff check . && ruff format --check .` | ✅ sin errores |
| `mypy panda config` | ✅ Success: no issues found |
| `pytest -q` | ✍️ ✅ 33 passed, 1 failed en 7.38 s |
| `coverage report --include="panda/dominio/*"` | No data found |
| `python manage.py makemigrations --check --dry-run` | ✅ No changes detected |
| `lint-imports` | N/A |
| `python manage.py spectacular --validate --fail-on-warn` | N/A (el contrato OpenAPI se activa con SCRUM-428) |

**Pruebas nuevas o modificadas:**

| Prueba | Qué verifica | Resultado |
|---|---|---|
| `test_ejemplo_450_kcal_70_kg_moderado` (`tests/dominio/test_recomendacion.py`) | Ejemplo 450 kcal 70 kg moderado | ✅ |
| `test_sedentario_no_recibe_vigorosas` (`tests/dominio/test_recomendacion.py`) | Sedentario no recibe vigorosas | ✅ |
| `test_preferidas_van_primero` (`tests/dominio/test_recomendacion.py`) | Preferidas van primero | ✅ |
| `test_descarta_si_supera_180_min` (`tests/dominio/test_recomendacion.py`) | Descarta si supera 180 min | ✅ |
| `test_cero_kcal_devuelve_lista_vacia_con_mensaje` (`tests/dominio/test_recomendacion.py`) | Cero kcal devuelve lista vacia con mensaje | ✅ |
| `test_limites_de_seguridad` (`tests/dominio/test_recomendacion.py`) | Límites de seguridad | ✅ |

### 3.2 Manuales (curl, Bruno o Swagger)

| # | Caso | Pasos | Esperado | Obtenido | ✅ / ❌ |
|---|---|---|---|---|---|
| 1 | Ejemplo 70 kg, moderado, 450 kcal | `recomendar(450, 70, MODERADO, cat, set())` | Caminar 160 min en 4 sesiones (490 kcal); Bici 65 min (462 kcal) | Caminar 160 min en 4 sesiones (490 kcal); Bici 65 min (462 kcal) | ✅ |

### 3.3 Evidencia

```text
FAILED tests/catalogos/test_cargar_catalogos.py::test_los_csv_del_repositorio_cumplen_las_restricciones - AssertionError: T-138: el catálogo debe tener al menos 50 alimentos
1 failed, 33 passed, 1 warning in 7.38s
```

## 4. Riesgos y reversión

- **Riesgos:** Ninguno en tiempo de ejecución.
- **Cómo revertir:** `git revert` del squash.

## 5. Checklist del PR (Definition of Done)

- [ ] El título del PR y los commits siguen `tipo(alcance): SCRUM-447 descripción`
- [ ] Una sola historia en la rama; base `develop`
- [ ] Hay pruebas para el comportamiento nuevo y toda la suite está en verde
- [x] `openapi.yaml` regenerado si cambió un serializer o una vista — no aplica
- [x] Migraciones creadas en el mismo commit que su modelo y revisadas con `sqlmigrate` — no aplica
- [x] `.env.example` actualizado si hay variables nuevas — no aplica
- [ ] Sin secretos ni datos personales en el código, los logs ni este documento
- [ ] Subtareas de Jira en *En revisión* y enlazadas al PR