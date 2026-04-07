"""Dimensoes por formato — fonte unica de verdade.

Todos os arquivos que precisam de dimensoes importam daqui.
Le de configs/formatos.json como fonte primaria; FORMATS dict como fallback.
"""

import json
from pathlib import Path

FORMATS = {
    "carrossel": {"width": 1080, "height": 1350, "ratio": "4:5", "label": "portrait"},
    "post_unico": {"width": 1080, "height": 1080, "ratio": "1:1", "label": "square"},
    "thumbnail_youtube": {"width": 1280, "height": 720, "ratio": "16:9", "label": "landscape"},
    "capa_reels": {"width": 1080, "height": 1920, "ratio": "9:16", "label": "tall portrait"},
}

_FORMATOS_PATH = Path(__file__).parent.parent / "configs" / "formatos.json"
_json_cache: dict | None = None


def _carregar_dims_mongo(formato: str) -> dict | None:
    """Tenta ler dimensoes do MongoDB; retorna None se falhar."""
    try:
        from data.repositories.mongo.formato_repository import FormatoRepository
        fmt = FormatoRepository.buscar(formato)
        if fmt and "dimensoes" in fmt:
            return fmt["dimensoes"]
    except Exception:
        pass
    return None


def _carregar_dims_json(formato: str) -> dict | None:
    """Tenta ler dimensoes do JSON; retorna None se falhar."""
    global _json_cache
    try:
        if _json_cache is None:
            if _FORMATOS_PATH.exists():
                _json_cache = json.loads(_FORMATOS_PATH.read_text(encoding="utf-8"))
            else:
                _json_cache = {"formatos": []}
        for f in _json_cache.get("formatos", []):
            if f["id"] == formato:
                return f["dimensoes"]
    except Exception:
        pass
    return None


def get_dims(formato: str) -> dict:
    """Retorna {width, height, ratio, label} do formato. Mongo > JSON > dict hardcoded."""
    # Tentar Mongo primeiro
    dims = _carregar_dims_mongo(formato)
    if dims:
        return dims
    # Fallback JSON
    dims = _carregar_dims_json(formato)
    if dims:
        return dims
    # Fallback dict hardcoded
    return FORMATS.get(formato, FORMATS["carrossel"])


def get_prompt_size_str(formato: str) -> str:
    """Retorna string pro prompt do Gemini, ex: '1080x1350px, 4:5 portrait'."""
    d = get_dims(formato)
    return f"{d['width']}x{d['height']}px, {d['ratio']} {d['label']}"


def get_page_mm(formato: str) -> tuple[float, float]:
    """Retorna (width_mm, height_mm) pra geracao de PDF."""
    d = get_dims(formato)
    # 1px = 0.2mm a 127 DPI (padrao jsPDF)
    scale = 0.2
    return (d["width"] * scale, d["height"] * scale)
