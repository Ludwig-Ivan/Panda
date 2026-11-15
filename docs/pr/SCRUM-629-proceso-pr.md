# SCRUM-629 · Establecer el proceso de PR con documentación de cambios

| Campo | Valor |
|---|---|
| Historia | [HU-66](https://desarrollowebleo.atlassian.net/browse/SCRUM-629) · Establecer el proceso de PR con documentación de cambios |
| Subtareas | T-161, T-165 |
| Rama → base | `chore/SCRUM-629-proceso-pr` → `develop` |
| Pull Request | #4 |
| Autor / Revisor | Ludwig Ivan Ortiz Sierra / ... |
| Fecha | 2026-11-15 |

## 1. Qué cambió

**Resumen** (1 a 3 líneas): Se agregaron las plantillas de la documentacion de PR.


**Tipo de cambio:**

- [ ] Funcionalidad nueva
- [ ] Corrección de un bug
- [ ] Refactor sin cambio de comportamiento
- [ ] Solo pruebas
- [ ] Infraestructura o CI
- [x] Documentación

**Impacto en contratos:**

| Área | ¿Cambia? | Detalle |
|---|---|---|
| API (`openapi.yaml`) | Sí / ~~No~~ | ... |
| Base de datos | Sí / ~~No~~ | ... |
| Configuración | Sí / ~~No~~ | .. |
| Dependencias | Sí / ~~No~~ | .. |

## 2. Dónde cambió

| Archivo | Cambio | Descripción |
|---|---|---|
| `docs/prs/_plantilla.md` | A | Plantilla del PR de documentacion |
| `.github/pull_request_template.md` | A | Plantilla de PR de Github |

**Migraciones:** `<app>/000N_<nombre>.py` · reversible: sí / no · revisada con `sqlmigrate`: sí / no
**Endpoints:** `<MÉTODO> /api/v1/<ruta>` → <qué hace y qué códigos de respuesta devuelve>
**Variables de entorno:** `<NOMBRE>` (valor por defecto, dónde se configura en cada entorno)

## 3. Pruebas y resultados

### 3.1 Automáticas

| Comando | Resultado |
|---|---|
| `ruff check . && ruff format --check .` | ✅ / ❌ <detalle> |
| `mypy panda config` | ✅ / ❌ |
| `pytest -q` | ✅ <N> passed, <M> failed en <t> s |
| `coverage report --include="panda/dominio/*"` | <xx> % |
| `python manage.py makemigrations --check --dry-run` | ✅ No changes detected |
| `lint-imports` | ✅ <n> kept, 0 broken |
| `python manage.py spectacular --validate --fail-on-warn` | ✅ / N/A |
| CI del PR (`calidad-y-pruebas`, `secretos`, `documentacion-pr`) | ✅ / ❌ <enlace a la ejecución> |

**Pruebas nuevas o modificadas:**

| Prueba | Qué verifica | Resultado |
|---|---|---|
| `test_<nombre>` | <comportamiento o regla> | ✅ |

### 3.2 Manuales (curl, Bruno o Swagger)

| # | Caso | Pasos | Esperado | Obtenido | ✅ / ❌ |
|---|---|---|---|---|---|
| 1 | <caso feliz> | <comando o pasos> | <código y cuerpo> | <lo que pasó> | ✅ |
| 2 | <caso de error> | | | | |

### 3.3 Evidencia

Salida resumida, sin tokens, correos reales, contraseñas ni datos personales:

```text
<pega aquí las últimas líneas de pytest, la cobertura o la respuesta de curl>
```

## 4. Riesgos y reversión

- **Riesgos:** <qué podría fallar en Staging o Producción y cómo se detectaría>
- **Cómo revertir:** `git revert <sha>` del squash; ¿la migración es reversible? <sí/no; pasos si no lo es>

## 5. Checklist del PR (Definition of Done)

- [ ] El título del PR y los commits siguen `tipo(alcance): SCRUM-<n> descripción`
- [ ] Una sola historia en la rama; base `develop`
- [ ] Hay pruebas para el comportamiento nuevo y toda la suite está en verde
- [ ] `openapi.yaml` regenerado si cambió un serializer o una vista
- [ ] Migraciones creadas en el mismo commit que su modelo y revisadas con `sqlmigrate`
- [ ] `.env.example` actualizado si hay variables nuevas
- [ ] Sin secretos ni datos personales en el código, los logs ni este documento
- [ ] Subtareas de Jira en *En revisión* y enlazadas al PR
