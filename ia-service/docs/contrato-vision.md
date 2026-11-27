# Contrato de visión entre el servicio de IA y el backend (SCRUM-768)

| Campo | Valor |
|---|---|
| **Estado** | Propuesta: pendiente de acordar con Iván (backend) |
| **Autora** | Estefanía López Rivas |
| **Bloquea** | HU-74 (SCRUM-637), el adaptador real en el backend |
| **Fecha** | 2026-11-25 |

## 1. El problema

- **Lo que espera el backend:** el contrato `VisionProvider` (Guía de Backend, Paso 12.1) recibe una **lista de
  alimentos**, cada uno con nombre, gramos y confianza. Con esa lista el backend busca cada alimento en el catálogo y
  calcula las kcal. Así lo fija AD-06: *las kcal las calcula Panda, no el modelo*.
- **Lo que produce el modelo:** `siglip2-caloriek-n5k` devuelve **totales del platillo**: kcal, masa, grasa,
  carbohidratos y proteína. No devuelve lista de alimentos ni confianza por alimento.

Los dos formatos no encajan, y hay que elegir cómo resolverlo antes de que Estefanía escriba el adaptador
(SCRUM-637).

## 2. Lo que ya entrega el servicio de IA (implementado)

`POST /v1/vision/estimar` · `multipart/form-data` con el campo `foto` · header `X-API-Key`

```json
{
  "modelo": { "nombre": "siglip2-caloriek-n5k", "version": "3f9a1c0b7d2e" },
  "nutrientes": {
    "calorias":     { "valor": 412.3, "min": 340.6, "max": 484.0, "unidad": "kcal", "pct_mae": 17.4 },
    "masa":         { "valor": 298.1, "min": 249.9, "max": 346.3, "unidad": "g",    "pct_mae": 16.2 },
    "grasa":        { "valor": 15.2,  "min": 11.3,  "max": 19.1,  "unidad": "g",    "pct_mae": 25.9 },
    "carbohidrato": { "valor": 48.7,  "min": 37.4,  "max": 60.0,  "unidad": "g",    "pct_mae": 23.1 },
    "proteina":     { "valor": 22.9,  "min": 17.6,  "max": 28.2,  "unidad": "g",    "pct_mae": 23.3 }
  },
  "avisos": [
    "Las calorías y los nutrientes son una estimación aproximada a partir de la foto.",
    "Panda no sustituye la orientación de un profesional de la salud o la nutrición."
  ],
  "latencia_ms": 812
}
```

| Código | Cuándo |
|---|---|
| `401 UNAUTHORIZED` | Falta `X-API-Key` o no es válida |
| `413 PAYLOAD_TOO_LARGE` | Más de 10 MB |
| `415 UNSUPPORTED_MEDIA_TYPE` | No es JPEG, PNG ni WebP (se revisa el contenido, no la extensión) |
| `422 IMAGE_TOO_SMALL` / `VALIDATION_ERROR` | Menos de 640×480, o falta el campo `foto` |
| `503 MODEL_NOT_READY` | El modelo sigue cargando o falló al verificar los pesos |

Los errores usan el mismo formato que la API de Panda: `{"error": {"code", "message", "details"}}`.

## 3. Opciones

### Opción A: el contrato acepta totales (recomendada para el MVP)

- `ResultadoVision` agrega un campo opcional `totales` con las kcal y su rango. El adaptador lo llena y deja
  `alimentos` vacío.
- Cuando vienen totales, `EstimationService` crea **un solo item**:
  - nombre: «Platillo (estimado por foto)»;
  - `gramos` = masa estimada;
  - `kcal_100g` = kcal ÷ masa × 100;
  - `fuente_kcal = estimado_ia`, lo que activa `requiere_revision = true`.
- El usuario sigue pudiendo corregir: cambiar la porción, reemplazar el item por alimentos del catálogo o agregar
  más alimentos.
- **AD-06 cambia:** las kcal las estima el modelo. El backend conserva el cálculo cuando el usuario corrige.

| A favor | En contra |
|---|---|
| Usa el modelo que ya existe, con 17.4 % de %MAE en calorías | No hay desglose por alimento, que era la experiencia diseñada en la UI |
| Cabe en el calendario (cierre el 11 de diciembre) | La métrica de la PoC «identificación correcta del alimento principal» (≥ 80 %) no se puede medir |
| Las correcciones y la auditoría del backend siguen funcionando igual | Requiere cambios pequeños en SCRUM-636 (backend) y en AD-06 |

### Opción B: agregar un paso que identifique alimentos

- Un modelo multimodal (por ejemplo Qwen-VL) o un clasificador lista los alimentos con gramos y confianza.
- El modelo de totales queda como verificación o se descarta.
- **AD-06 no cambia.**

| A favor | En contra |
|---|---|
| Respeta el diseño original y la UI de revisión por alimento | Es un segundo modelo: entrenamiento o evaluación, latencia y costo extra |
| Se puede medir la identificación (PoC-01) | No hay tiempo realista antes del 11 de diciembre |

## 4. Recomendación

**Opción A para el MVP, y la B como mejora posterior.** El cambio en el backend es acotado: un campo opcional en
`ResultadoVision` y una rama en `EstimationService`. El resto del flujo no cambia: correcciones, recomendación,
historial y auditoría.

## 5. Qué hay que decidir con Iván

1. ¿Opción A o B?
2. Si es A:
   - el texto exacto del nombre del item;
   - si el rango del backend usa el ±%MAE del modelo o su propio factor por confianza;
   - la redacción nueva de AD-06.
3. ¿Quién actualiza el Architecture Document y la API Specification?

Cuando haya decisión, se registra en la sección 6 y se cierra SCRUM-768.

## 6. Decisión

*Pendiente.*
