## Historia

SCRUM-<n> · <título de la historia> · Subtareas: T-xxx, T-yyy

## Documentación del PR

`docs/prs/SCRUM-<n>-<descripcion>.md` ← obligatoria; la verifica el check `documentacion-pr`.
Usa `docs/prs/_plantilla.md`: qué cambió, dónde cambió y pruebas con resultados.

## Resumen

<!-- 1 a 3 líneas: qué cambió y por qué. El detalle va en el documento del PR. -->

## Cómo probarlo

<!-- Comandos o pasos para que el revisor lo compruebe en local o en Staging. -->

## Checklist

- [ ] Título `tipo(alcance): SCRUM-<n> descripción`
- [ ] CI en verde: `calidad-y-pruebas`, `secretos`, `documentacion-pr`
- [ ] Documento del PR con los resultados reales de las pruebas
- [ ] `openapi.yaml` regenerado (si cambió la API)
- [ ] Sin secretos ni datos personales
