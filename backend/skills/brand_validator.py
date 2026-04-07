from PIL import Image
import io
import base64
import json
from pathlib import Path


CONFIGS_PATH = Path(__file__).parent.parent / "configs"


def validar(image_base64: str, formato: str) -> dict:
    """Valida imagem contra brand_palette.json.

    Retorna:
        {"valido": bool, "erros": list[str]}
    """
    palette = _carregar_palette()
    erros = []

    # Decodificar imagem
    img_data = image_base64.split(",")[1] if "," in image_base64 else image_base64
    img = Image.open(io.BytesIO(base64.b64decode(img_data)))

    # Validar aspect ratio
    dims = _carregar_dimensions()
    esperado = dims.get(formato, {})
    if esperado:
        w_esperado, h_esperado = esperado["width"], esperado["height"]
        ratio_esperado = w_esperado / h_esperado
        ratio_atual = img.width / img.height
        if abs(ratio_atual - ratio_esperado) > 0.05:
            erros.append(f"Aspect ratio incorreto: esperado {ratio_esperado:.2f}, atual {ratio_atual:.2f}")

    # Validar dimensoes
    if esperado and (img.width != w_esperado or img.height != h_esperado):
        erros.append(f"Dimensoes incorretas: esperado {w_esperado}x{h_esperado}, atual {img.width}x{img.height}")

    return {"valido": len(erros) == 0, "erros": erros}


def _carregar_palette() -> dict:
    path = CONFIGS_PATH / "brand_palette.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _carregar_dimensions() -> dict:
    path = CONFIGS_PATH / "dimensions.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
