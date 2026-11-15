# SCRUM-<n> · <título del PR sin el prefijo tipo(alcance)>

| Campo | Valor |
|---|---|
| Historia | [SCRUM-<n>](https://desarrollowebleo.atlassian.net/browse/SCRUM-<n>) · <título de la historia> |
| Subtareas | T-xxx, T-yyy |
| Rama → base | `<tipo>/SCRUM-<n>-<descripcion>` → `develop` |
| Pull Request | #<número> |
| Autor / Revisor | <nombre> / <nombre> |
| Fecha | AAAA-MM-DD |
| Guía de Desarrollo del Backend | Fase <N>, Pasos <N.x>–<N.y> |

## 1. Qué cambió

**Resumen** (1 a 3 líneas): <qué hace ahora el sistema que antes no hacía, o qué se corrigió>.

**Por qué:** <problema o requisito que resuelve: RF-xx, RNF-xx, RD-xx, criterio de aceptación de la historia>.

**Tipo de cambio:**

- [ ] Funcionalidad nueva
- [ ] Corrección de un bug
- [ ] Refactor sin cambio de comportamiento
- [ ] Solo pruebas
- [ ] Infraestructura o CI
- [ ] Documentación

**Impacto en contratos:**

| Área | ¿Cambia? | Detalle |
|---|---|---|
| API (`openapi.yaml`) | Sí / No | <endpoints nuevos o modificados; ¿rompe compatibilidad?> |
| Base de datos | Sí / No | <migraciones, constraints, índices, datos> |
| Configuración | Sí / No | <variables de entorno nuevas; ya están en `.env.example`> |
| Dependencias | Sí / No | <paquete y versión> |

## 2. Dónde cambió

| Archivo | Cambio | Descripción |
|---|---|---|
| `backend/panda/<app>/<archivo>.py` | A / M / D | <qué contiene o qué se modificó> |
| `backend/tests/<carpeta>/test_<tema>.py` | A | <qué verifica> |

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
