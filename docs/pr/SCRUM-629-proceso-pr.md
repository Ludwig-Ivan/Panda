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

**Resumen**: Se agregaron las plantillas de la documentacion de PR.


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


## 3. Pruebas y resultados
- Revisar los directorios correspondientes

### 3.1 Automáticas

| Comando | Resultado |
|---|---|
| ... | ... |

| Prueba | Qué verifica | Resultado |
|---|---|---|
| ... | ... | ...

### 3.2 Manuales (curl, Bruno o Swagger)

| # | Caso | Pasos | Esperado | Obtenido | ✅ / ❌ |
|---|---|---|---|---|---|
|...|...|...|...|...|...|

### 3.3 Evidencia

Revisar la ruta de la documentacion.


## 4. Riesgos y reversión

...

## 5. Checklist del PR (Definition of Done)

- [x] El título del PR y los commits siguen `tipo(alcance): SCRUM-<n> descripción`
- [x] Una sola historia en la rama; base `develop`
- [x] Hay pruebas para el comportamiento nuevo y toda la suite está en verde
- [x] `openapi.yaml` regenerado si cambió un serializer o una vista
- [x] Migraciones creadas en el mismo commit que su modelo y revisadas con `sqlmigrate`
- [x] `.env.example` actualizado si hay variables nuevas
- [x] Sin secretos ni datos personales en el código, los logs ni este documento
- [x] Subtareas de Jira en *En revisión* y enlazadas al PR
