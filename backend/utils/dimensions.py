"""Dimensoes por formato — fonte unica de verdade.

Todos os arquivos que precisam de dimensoes importam daqui.
Nunca hardcodar 1080x1350 em outro lugar.
"""

FORMATS = {
    "carrossel": {"width": 1080, "height": 1350, "ratio": "4:5", "label": "portrait"},
    "post_unico": {"width": 1080, "height": 1080, "ratio": "1:1", "label": "square"},
    "thumbnail_youtube": {"width": 1280, "height": 720, "ratio": "16:9", "label": "landscape"},
    "capa_reels": {"width": 1080, "height": 1920, "ratio": "9:16", "label": "tall portrait"},
}


def get_dims(formato: str) -> dict:
    """Retorna {width, height, ratio, label} do formato."""
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
