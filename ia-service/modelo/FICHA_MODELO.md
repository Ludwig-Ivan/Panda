# Ficha del modelo: `siglip2-caloriek-n5k` v1

| Campo | Valor |
|---|---|
| **Qué estima** | Totales de un platillo a partir de una foto: calorías (kcal), masa, grasa, carbohidratos y proteína (g) |
| **Qué NO hace** | No identifica alimentos individuales, no detecta si la foto no es comida, no estima por porción |
| **Responsable** | Estefanía López Rivas (modelo de IA) |
| **Origen** | `comida.ipynb`, Opción A, entrenado en Colab el 2026-11-12 |
| **Uso en Panda** | `POST /v1/vision/estimar` del servicio de IA (`ia-service/`) |

## Artefactos

| Archivo | SHA-256 | Dónde está |
|---|---|---|
| `best.pt` (375 MB) | `95cff0515105e5774a0a8ff63a3a686373469dd9ae9ecf624e088e1f07c1c7c6` (374,767,152 bytes) | Drive: `MyDrive/n5k_runs/caloriek_ft/best.pt` → release `modelo-v1` |
| `test_metrics.json` | `40fb8533c8ea88ca997a208b400f8ec5a605e601a7c8d167b9ac5104d9eca33e` | `modelo/test_metrics.json` (en este repo) |
| `test_predictions.csv` | `a11999ed684edf6c69ef5c9fffbb76584694826c441f38656e47bc7f4501fbc0` | Drive, misma carpeta (507 platillos del test) |

El servicio solo carga `best.pt` si su SHA-256 coincide con `IA_MODELO_SHA256`. La versión que reporta en cada
respuesta (`modelo.version`) son los primeros 12 caracteres de ese hash.

## Arquitectura

- **Backbone:** SigLIP2 base, parche 16, entrada 224×224 (`google/siglip2-base-patch16-224`, Apache-2.0).
- **Cabeza:** `LayerNorm → Linear(768) → GELU → Dropout(0.15) → Linear(256) → GELU → Dropout(0.10) → Linear(5)`,
  con `softplus` a la salida, de modo que nunca hay valores negativos. Es la misma cabeza de CalorieK.
- **Inicialización (Opción A):** pesos de [`Dralkh/CalorieK`](https://huggingface.co/Dralkh/CalorieK), reordenando
  las salidas a `[calorias, masa, grasa, carbohidrato, proteina]`.
- **Preprocesamiento:** RGB → [0, 1] → redimensionar a 224×224 con antialias → `(x − 0.5) / 0.5`.

## Entrenamiento

| Parámetro | Valor |
|---|---|
| Datos | Nutrition5k, cámara cenital RGB (`realsense_overhead`), splits oficiales |
| Platillos | train 2 494 · val 261 (10 % del train) · test 507. Se omitieron 1 506 sin foto en el bucket |
| Épocas | 15, con 1 de calentamiento y coseno |
| Learning rate | cabeza 2e-4 · backbone 1e-5 (AdamW, weight decay 1e-4) |
| Batch | 32 |
| Pérdida | SmoothL1 (β = 0.1) con cada nutriente dividido entre su promedio del train |
| Aumento de datos | Volteos, rotación ±180°, brillo, contraste, saturación y tono |
| Selección | Mejor época por %MAE medio en validación |

## Resultados en el test oficial (507 platillos)

| Nutriente | MAE | %MAE |
|---|---|---|
| Calorías | 44.4 kcal | 17.4 % |
| Masa | 32.1 g | 16.2 % |
| Grasa | 3.3 g | 25.9 % |
| Carbohidratos | 4.5 g | 23.1 % |
| Proteína | 4.1 g | 23.3 % |
| **%MAE medio** | | **21.2 %** |

Como referencia, CalorieK sin ajustar daba 40.4 % de %MAE medio en validación.

**Rango que devuelve el servicio:** `valor × (1 ± %MAE)`, por nutriente. Para calorías es ±17.4 %.

**Umbral de la PoC (SRS 3.5.8):** MAPE ≤ 25 % en calorías. El %MAE del test (17.4 %) no es exactamente el MAPE: el
MAPE promedia el error relativo de cada platillo, y en los platillos pequeños ese error crece. La comparación formal
contra el umbral es T-113 (SCRUM-613).

## Limitaciones conocidas

1. **Dominio:** Nutrition5k son platillos de cafetería en EE. UU., fotografiados desde arriba con una cámara fija.
   Los platillos mexicanos, las fotos en ángulo y la luz de casa no están representados, así que el error real en
   Panda puede ser mayor. Lo mide T-112 (SCRUM-612) con el conjunto de referencia.
2. **Solo totales:** no hay lista de alimentos. Esto choca con el contrato `VisionProvider` del backend y con AD-06;
   ver `docs/contrato-vision.md` (SCRUM-768).
3. **No rechaza fotos que no son comida:** siempre devuelve números. La validación de formato y resolución sí está
   en el servicio.
4. **Licencias por confirmar antes de uso público (TBC-08):**
   - Nutrition5k: verificar su licencia en el repositorio oficial y citarlo.
   - La licencia de CalorieK no está confirmada. Hay que revisarla en su página de Hugging Face y, si no permite
     este uso, entrenar con la Opción B (desde SigLIP2 base).
   - El archivo de CalorieK pide `weights_only=False` al cargarlo, lo que ejecuta código del archivo. El servicio no
     lo carga: solo carga `best.pt` verificado por SHA-256.
