from PIL import Image
import io
import base64
import json
from pathlib import Path


CONFIGS_PATH = Path(__file__).parent.parent / "configs"


def validar(
    image_base64: str,
    formato: str,
    aspect_ratio: str | None = None,        # legado (ignorado); mantido pra compat
    exige_foto_criador: bool = True,        # legado (ignorado)
    exige_logo: bool = True,
    dimensao_id: str | None = None,         # legado (ignorado)
) -> dict:
    """Valida imagem contra brand_palette.json.

    Pos-pivot 2026-04-23: parametros legados `aspect_ratio`, `exige_foto_criador`
    e `dimensao_id` sao aceitos mas ignorados. Anuncio agora usa o mesmo
    validador do post_unico.

    Args:
        image_base64: imagem a validar.
        formato: carrossel, post_unico, thumbnail_youtube, capa_reels, anuncio.
        exige_logo: False desativa check de logo.

    Retorna:
        {"valido": bool, "erros": list[str]}
    """
    _palette = _carregar_palette()
    erros: list[str] = []

    # Decodificar imagem
    img_data = image_base64.split(",")[1] if "," in image_base64 else image_base64
    img = Image.open(io.BytesIO(base64.b64decode(img_data)))

    # Validar aspect ratio via dimensions.json (sempre objeto simples agora)
    dims = _carregar_dimensions()
    esperado = dims.get(formato) or {}
    if isinstance(esperado, dict) and esperado:
        w_esperado = esperado.get("width")
        h_esperado = esperado.get("height")
        if w_esperado and h_esperado:
            ratio_esperado = w_esperado / h_esperado
            ratio_atual = img.width / img.height
            if abs(ratio_atual - ratio_esperado) > 0.05:
                erros.append(
                    f"Aspect ratio incorreto: esperado {ratio_esperado:.2f}, atual {ratio_atual:.2f}"
                )
            if img.width != w_esperado or img.height != h_esperado:
                erros.append(
                    f"Dimensoes incorretas: esperado {w_esperado}x{h_esperado}, "
                    f"atual {img.width}x{img.height}"
                )

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
