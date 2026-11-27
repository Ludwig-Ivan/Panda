# tests/test_modelo.py
"""T-211: el port de NutritionModel y del preprocesamiento es equivalente al notebook.

Se usa un SigLIP diminuto con pesos aleatorios (sin red). El checkpoint se guarda con el mismo formato que la
sección 8 del notebook: {"model": state_dict, "config": {"img_size", "opcion", "vision_config"}}.
La equivalencia con los pesos reales (±1 %) la cubre tests/regresion/.
"""

import numpy as np
import pytest

torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")

from PIL import Image  # noqa: E402
from torchvision.transforms.v2 import functional as TF  # noqa: E402, N812

from app.vision import NUTRIENTES  # noqa: E402
from app.vision.estimador import EstimadorSiglip  # noqa: E402
from app.vision.modelo import NutritionModel, cargar_checkpoint  # noqa: E402
from app.vision.preprocesamiento import a_tensor  # noqa: E402

CONFIG_DIMINUTA = {
    "hidden_size": 32,
    "intermediate_size": 64,
    "num_hidden_layers": 1,
    "num_attention_heads": 2,
    "image_size": 32,
    "patch_size": 16,
}
IMG_SIZE = 32


def predecir_como_el_notebook(model, path, img_size):
    """Copia literal de la lógica de `predecir()` (comida.ipynb, sección 10)."""
    img = Image.open(path).convert("RGB")
    x = torch.from_numpy(np.array(img)).permute(2, 0, 1).float() / 255.0
    x = TF.resize(x, [img_size] * 2, antialias=True)
    x = ((x - 0.5) / 0.5)[None]
    with torch.no_grad():
        y = model(x)[0].tolist()
    return dict(zip(NUTRIENTES, y, strict=True))


@pytest.fixture
def checkpoint(tmp_path):
    torch.manual_seed(0)
    modelo = NutritionModel(CONFIG_DIMINUTA)
    modelo.scale.copy_(torch.tensor([230.0, 200.0, 12.0, 19.0, 17.0]))  # como en la Opción B del notebook
    ruta = tmp_path / "best.pt"
    config = {"img_size": IMG_SIZE, "opcion": "A", "vision_config": modelo.backbone.config.to_dict()}
    torch.save({"model": modelo.state_dict(), "config": config}, ruta)
    return ruta, modelo.eval()


@pytest.fixture
def foto(tmp_path):
    rng = np.random.default_rng(0)
    ruta = tmp_path / "plato.png"
    Image.fromarray(rng.integers(0, 255, (480, 640, 3), dtype=np.uint8)).save(ruta)
    return ruta


def test_las_llaves_del_state_dict_coinciden_con_el_notebook(checkpoint):
    ruta, _ = checkpoint
    llaves = set(torch.load(ruta, weights_only=True)["model"])
    assert "scale" in llaves and "head.net.7.weight" in llaves  # mismos nombres que la sección 6 del notebook


@pytest.mark.parametrize(
    "convertir",
    [
        lambda k: k.replace("backbone.", "backbone.vision_model.", 1) if k.startswith("backbone.") else k,  # 5.x → 4.x
        lambda k: k,
    ],
)
def test_carga_checkpoints_de_transformers_4_y_5(checkpoint, tmp_path, convertir):
    ruta, original = checkpoint
    ckpt = torch.load(ruta, weights_only=True)
    ckpt["model"] = {convertir(k): v for k, v in ckpt["model"].items()}
    otra = tmp_path / "otra_version.pt"
    torch.save(ckpt, otra)
    modelo, _ = cargar_checkpoint(otra, torch.device("cpu"))
    x = torch.zeros(1, 3, IMG_SIZE, IMG_SIZE)
    with torch.no_grad():
        assert torch.allclose(modelo(x), original(x))


def test_checkpoint_de_otra_arquitectura_falla_con_mensaje_claro(checkpoint, tmp_path):
    from app.vision.modelo import ErrorCheckpoint

    ruta, _ = checkpoint
    ckpt = torch.load(ruta, weights_only=True)
    ckpt["model"] = {k: v for k, v in ckpt["model"].items() if not k.startswith("head.")}
    rota = tmp_path / "rota.pt"
    torch.save(ckpt, rota)
    with pytest.raises(ErrorCheckpoint, match="no coinciden"):
        cargar_checkpoint(rota, torch.device("cpu"))


def test_carga_el_checkpoint_con_weights_only(checkpoint):
    ruta, original = checkpoint
    modelo, img_size = cargar_checkpoint(ruta, torch.device("cpu"))
    assert img_size == IMG_SIZE and not modelo.training
    assert torch.equal(modelo.scale, original.scale)


def test_preprocesamiento_identico_al_notebook(foto):
    esperado = TF.resize(
        torch.from_numpy(np.array(Image.open(foto).convert("RGB"))).permute(2, 0, 1).float() / 255.0,
        [IMG_SIZE, IMG_SIZE],
        antialias=True,
    )
    esperado = ((esperado - 0.5) / 0.5)[None]
    assert torch.equal(a_tensor(Image.open(foto), IMG_SIZE), esperado)


def test_prediccion_del_servicio_igual_a_la_del_notebook(checkpoint, foto):
    ruta, original = checkpoint
    notebook = predecir_como_el_notebook(original, foto, IMG_SIZE)
    servicio = EstimadorSiglip.desde_checkpoint(ruta, "cpu", "a" * 64).predecir(Image.open(foto))
    for n in NUTRIENTES:
        assert servicio[n] == pytest.approx(notebook[n], rel=1e-5)
        assert servicio[n] >= 0  # softplus × scale


def test_version_es_el_prefijo_del_sha(checkpoint):
    ruta, _ = checkpoint
    assert EstimadorSiglip.desde_checkpoint(ruta, "cpu", "0123456789abcdef" * 4).version == "0123456789ab"


def test_servicio_completo_con_el_modelo_real(checkpoint, tmp_path):
    """Arranque real: descarga por file://, verifica el SHA-256, carga en segundo plano, /ready y /v1/vision/estimar."""
    import hashlib

    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import create_app

    from .conftest import CLAVE, esperar_listo, imagen_bytes

    ruta, _ = checkpoint
    sha = hashlib.sha256(ruta.read_bytes()).hexdigest()
    settings = Settings(
        api_keys=[CLAVE],
        modelo="siglip",
        modelo_url=f"file://{ruta}",
        modelo_sha256=sha,
        modelo_dir=tmp_path / "cache",
        dispositivo="cpu",
    )
    with TestClient(create_app(settings)) as c:
        esperar_listo(c, segundos=60)
        r = c.post(
            "/v1/vision/estimar", files={"foto": ("p.jpg", imagen_bytes(), "image/jpeg")}, headers={"X-API-Key": CLAVE}
        )
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["modelo"] == {"nombre": "siglip2-caloriek-n5k", "version": sha[:12]}
    kcal = d["nutrientes"]["calorias"]
    assert kcal["min"] <= kcal["valor"] <= kcal["max"]


def test_servicio_no_arranca_con_pesos_alterados(checkpoint, tmp_path):
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import create_app

    from .conftest import CLAVE

    ruta, _ = checkpoint
    settings = Settings(
        api_keys=[CLAVE],
        modelo="siglip",
        modelo_url=f"file://{ruta}",
        modelo_sha256="0" * 64,
        modelo_dir=tmp_path / "cache",
        dispositivo="cpu",
    )
    import time

    with TestClient(create_app(settings)) as c:
        limite = time.monotonic() + 30
        while c.get("/ready").json()["componentes"].get("vision") == "cargando" and time.monotonic() < limite:
            time.sleep(0.05)
        r = c.get("/ready")
        assert r.status_code == 503 and r.json()["componentes"]["vision"] == "error"
