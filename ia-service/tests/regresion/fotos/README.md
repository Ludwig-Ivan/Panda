# Fotos fijas para la regresión (T-214)

Coloca aquí **10 fotos de platillos** (JPEG, PNG o WebP, al menos 640×480). No uses fotos con rostros ni datos
personales: esta carpeta se versiona.

Las fotos no deben tener orientación EXIF girada. El servicio corrige la orientación y el notebook no, así que con
una foto girada los dos verían imágenes distintas.

## Generar `esperado.json` desde el notebook

En Colab, con el mismo `best.pt` que se publicó (sección 10 ya ejecutada para tener `predecir`), sube las 10 fotos
y ejecuta:

```python
import json
from google.colab import files

esperado = {}
for nombre in files.upload():
    esperado[nombre] = {k: round(v, 4) for k, v in predecir(nombre).items()}
json.dump(esperado, open("esperado.json", "w"), indent=2, ensure_ascii=False)
files.download("esperado.json")
```

Copia `esperado.json` a esta carpeta y corre:

```bash
export IA_MODELO_PATH=/ruta/a/best.pt
pytest -m regresion -s
```
