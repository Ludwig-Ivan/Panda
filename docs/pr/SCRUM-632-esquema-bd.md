# SCRUM-632 · esquema completo con constraints, índices y on delete

| Campo | Valor |
|---|---|
| Historia | [SCRUM-632](<https://desarrollowebleo.atlassian.net/browse/SCRUM-632>) · Implementar el esquema de base de datos en Django |
| Subtareas | T-179, T-180, T-181, T-182, T-183, T-184 |
| Rama → base | `feature/SCRUM-632-esquema-bd` → `develop` |
| Pull Request | #9 |
| Autor / Revisor | Ludwig Iván Ortiz Sierra |
| Fecha | 2026-11-16 |

## 1. Qué cambió

**Resumen:** Esquema completo de la BD en Django: usuario propio, perfil, consentimientos, catálogos, preferencias, comidas, correcciones y recomendaciones, con constraints, índices GIN y `ON DELETE` también en PostgreSQL.

**Por qué:** Diseño de Base de Datos §4–§7; ajustes 1, 2 y 5 de la sección 0.4 (enumeraciones a nivel de módulo, correo único en minúsculas, tokens al borrar cuenta).

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
| Base de datos | Sí | 7 migraciones nuevas; extensiones `pg_trgm` y `unaccent`; CHECK de rangos; índices GIN trigram y de alias; FK con `ON DELETE` en la BD; tabla `django_cache` |
| Configuración | No | — |
| Dependencias | No | — |

## 2. Dónde cambió

| Archivo | Cambio | Descripción |
|---|---|---|
| `backend/panda/identidad/models.py` | A | Modelos |
| `backend/config/urls.py` | A | Versión temporal; la definitiva está en la Fase 14 |
| `backend/panda/estimacion/resiliencia.py` | A | Provisional; se completa en la Fase 12 |
| `backend/panda/dominio/texto.py` | A | Normalización de texto (dominio puro) |
| `backend/panda/catalogos/migrations/0001_extensiones.py` | A | Migración de extensiones |
| `backend/panda/catalogos/models.py` | A | Modelos |
| `backend/panda/comidas/models.py` | A | Comidas, items y correcciones |
| `backend/panda/recomendacion/models.py` | A | Recomendaciones |
| `backend/panda/comidas/migrations/0002_on_delete_en_bd.py` | A | `ON DELETE` también en la base de datos |
| `backend/tests/db/test_esquema.py` | A | Pruebas de esta historia (bloque de cierre de la guía) |
| `backend/tests/conftest.py` | A | Fixtures compartidas del Paso 17.2 (T-184) |
| `backend/panda/identidad/migrations/0001_crear_usuarios_y_perfiles.py` | A | Migración generada con `makemigrations` |
| `backend/panda/catalogos/migrations/0002_crear_alimentos_y_actividades.py` | A | Migración generada con `makemigrations` |
| `backend/panda/identidad/migrations/0002_preferencias_actividad.py` | A | Migración generada con `makemigrations` |
| `backend/panda/comidas/migrations/0001_crear_comidas.py` | A | Migración generada con `makemigrations` |
| `backend/panda/recomendacion/migrations/0001_crear_recomendaciones.py` | A | Migración generada con `makemigrations` |
| `docs/prs/SCRUM-632-esquema-bd.md` | A | Este documento |

**Migraciones:** `identidad/0001_crear_usuarios_y_perfiles.py`, `catalogos/0001_extensiones.py`, `catalogos/0002_crear_alimentos_y_actividades.py`, `identidad/0002_preferencias_actividad.py`, `comidas/0001_crear_comidas.py`, `recomendacion/0001_crear_recomendaciones.py`, `comidas/0002_on_delete_en_bd.py` · reversible: sí (las `RunSQL` incluyen `reverse_sql`) · revisada con `sqlmigrate`: ✍️ sí/no
**Endpoints:** Ninguno
**Variables de entorno:** Ninguna

## 3. Pruebas y resultados

### 3.1 Automáticas

| Comando | Resultado |
|---|---|
| `ruff check . && ruff format --check .` | ✍️ ✅ sin errores |
| `mypy panda config` | ✍️ ✅ Success: no issues found |
| `pytest -q` | ✍️ ✅ <N> passed, 0 failed en <t> s |
| `coverage report --include="panda/dominio/*"` | ✍️ <xx> % |
| `python manage.py makemigrations --check --dry-run` | ✍️ ✅ No changes detected |
| `lint-imports` | ✍️ ✅ <n> kept, 0 broken |
| `python manage.py spectacular --validate --fail-on-warn` | N/A (el contrato OpenAPI se activa con SCRUM-428) |
| CI del PR (`calidad-y-pruebas`, `secretos`, `documentacion-pr`) | ✍️ ✅ <enlace a la ejecución> |

**Pruebas nuevas o modificadas:**

| Prueba | Qué verifica | Resultado |
|---|---|---|
| `test_email_se_guarda_en_minusculas` (`tests/db/test_esquema.py`) | Email se guarda en minúsculas | ✅ |
| `test_bd_rechaza_menores_de_edad` (`tests/db/test_esquema.py`) | BD rechaza menores de edad | ✅ |
| `test_bd_rechaza_perfil_fuera_de_rango` (`tests/db/test_esquema.py`) | BD rechaza perfil fuera de rango | ✅ |
| `test_intensidad_debe_ser_coherente_con_el_met` (`tests/db/test_esquema.py`) | Intensidad debe ser coherente con el MET | ✅ |
| `test_alimento_normaliza_nombre_y_alias` (`tests/db/test_esquema.py`) | Alimento normaliza nombre y alias | ✅ |
| `test_on_delete_definido_en_la_bd` (`tests/db/test_esquema.py`) | On delete definido en la BD | ✅ |
| `test_health_responde_ok` (`tests/db/test_esquema.py`) | Health responde ok | ✅ |

### 3.2 Manuales (curl, Bruno o Swagger)

| # | Caso | Pasos | Esperado | Obtenido | ✅ / ❌ |
|---|---|---|---|---|---|
| 1 | Tablas | `docker compose exec db psql -U panda -c "\dt"` | Tablas del Diseño de BD §6 + framework | Muestra las tablas | ✅ |
| 2 | ON DELETE | `\d comida_items` | `fk_comida_items_alimento ... ON DELETE SET NULL` | Muestra el fk | ✅ |
| 3 | CHECK | `INSERT` de actividad con MET 2.0 e intensidad `vigorosa` | Falla con `violates check constraint` | Falla | ✅ |
| 4 | Migraciones al día | `dc python manage.py makemigrations --check --dry-run` | *No changes detected* | No hay cambios detectados | ✅ |

### 3.3 Evidencia

```text
✍️ últimas líneas de `pytest`, la cobertura o la respuesta de `curl` (sin tokens, correos reales ni contraseñas)
```

## 4. Riesgos y reversión

- **Riesgos:** Es el PR más delicado: si se aplica `migrate` con otro `AUTH_USER_MODEL` habrá que recrear la BD. Las FK redefinidas a mano deben rehacerse si un `ForeignKey` cambia en el futuro (nota del Paso 7.4).
- **Cómo revertir:** En local/Staging: `migrate <app> zero` en orden inverso (todas tienen `reverse_sql`) y `git revert`. En Producción aún no hay datos.

## 5. Checklist del PR (Definition of Done)

- [ ] El título del PR y los commits siguen `tipo(alcance): SCRUM-632 descripción`
- [ ] Una sola historia en la rama; base `develop`
- [ ] Hay pruebas para el comportamiento nuevo y toda la suite está en verde
- [x] `openapi.yaml` regenerado si cambió un serializer o una vista — no aplica
- [ ] Migraciones creadas en el mismo commit que su modelo y revisadas con `sqlmigrate`
- [x] `.env.example` actualizado si hay variables nuevas — no aplica
- [ ] Sin secretos ni datos personales en el código, los logs ni este documento
- [ ] Subtareas de Jira en *En revisión* y enlazadas al PR