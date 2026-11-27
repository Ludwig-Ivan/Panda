# app/vision/preprocesamiento.py
"""Preprocesamiento idéntico a `predecir()` del notebook (sección 10).

RGB → tensor [0, 1] → resize a img_size×img_size con antialias → normalización (x − 0.5) / 0.5 que espera SigLIP2.
Cualquier cambio aquí rompe la equivalencia con el notebook (criterio de HU-83: mismo resultado ±1 %).
"""

import numpy as np
import torch
from PIL import Image
from torchvision.transforms.v2 import functional as TF  # noqa: N812


def a_tensor(imagen: Image.Image, img_size: int) -> torch.Tensor:
    x = torch.from_numpy(np.array(imagen.convert("RGB"))).permute(2, 0, 1).float() / 255.0
    x = TF.resize(x, [img_size, img_size], antialias=True)
    return ((x - 0.5) / 0.5)[None]
