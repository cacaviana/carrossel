"""Renderiza texto sobre imagem de fundo usando Pillow — modo upload sem avatar.

Sem Gemini, sem IA. Pillow puro: abre o fundo, desenha texto, retorna base64.
"""
import base64
import io
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONTS_DIR = Path(__file__).parent.parent / "assets" / "fonts"
FONT_TITLE = FONTS_DIR / "Outfit-SemiBold.ttf"
FONT_BODY = FONTS_DIR / "Outfit-Medium.ttf"


def _load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(path), size)
    except Exception:
        return ImageFont.load_default()


def _decode_b64(b64: str) -> Image.Image:
    raw = b64.split(",", 1)[1] if "," in b64 else b64
    return Image.open(io.BytesIO(base64.b64decode(raw))).convert("RGBA")


def _encode_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _draw_text_with_shadow(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str = "#FFFFFF",
    shadow_color: str = "#000000",
    shadow_offset: int = 3,
    anchor: str | None = None,
):
    """Desenha texto com sombra pra garantir legibilidade em qualquer fundo."""
    x, y = xy
    # Sombra
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color, anchor=anchor)
    # Texto principal
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)


def _make_gradient(w: int, h: int, posicao: str, peak_opacity: int = 180) -> Image.Image:
    """Cria gradiente que vai de escuro pra transparente — sem borda dura.

    posicao: 'topo', 'baixo' ou 'centro'
    """
    gradient = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y in range(h):
        if posicao == "topo":
            # Escuro no topo, desvanece pra baixo
            alpha = int(peak_opacity * (1 - y / h) ** 1.5)
        elif posicao == "baixo":
            # Escuro embaixo, desvanece pra cima
            alpha = int(peak_opacity * (y / h) ** 1.5)
        else:
            # Centro: escuro no meio, desvanece nas bordas
            dist = abs(y - h / 2) / (h / 2)
            alpha = int(peak_opacity * (1 - dist) ** 1.2)
        alpha = max(0, min(255, alpha))
        for x in range(w):
            gradient.putpixel((x, y), (0, 0, 0, alpha))
    return gradient


def _make_gradient_fast(w: int, h: int, posicao: str, peak_opacity: int = 180) -> Image.Image:
    """Versao rapida do gradiente usando linhas em vez de pixel a pixel."""
    gradient = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(gradient)
    for y in range(h):
        if posicao == "topo":
            alpha = int(peak_opacity * (1 - y / h) ** 1.5)
        elif posicao == "baixo":
            alpha = int(peak_opacity * (y / h) ** 1.5)
        else:
            dist = abs(y - h / 2) / (h / 2)
            alpha = int(peak_opacity * (1 - dist) ** 1.2)
        alpha = max(0, min(255, alpha))
        draw.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
    return gradient


def _wrap_and_draw(draw, headline, font, w, y_start, y_end, shadow_offset=4):
    """Quebra texto e desenha centralizado dentro da faixa y_start..y_end."""
    font_size = font.size if hasattr(font, 'size') else 40
    max_chars = max(12, w // (font_size // 2 + 2))
    lines = textwrap.wrap(headline, width=max_chars)
    if not lines:
        lines = [headline]

    line_height = int(font_size * 1.3)
    total_text_h = len(lines) * line_height
    # Centralizar verticalmente dentro da faixa
    y_center = (y_start + y_end) // 2
    y_first = y_center - total_text_h // 2

    for i, line in enumerate(lines):
        y = y_first + i * line_height
        _draw_text_with_shadow(draw, (w // 2, y), line, font, anchor="mt", shadow_offset=shadow_offset)


def render_texto_centralizado(bg_b64: str, headline: str, dims: dict) -> str:
    """Texto centralizado — ocupa o terco central da imagem (nonos 4 a 6)."""
    bg = _decode_b64(bg_b64).resize((dims["width"], dims["height"]), Image.LANCZOS)
    w, h = bg.size
    nono = h // 9

    # Gradiente no centro (nonos 3 a 7 pra dar respiro)
    gradient = _make_gradient_fast(w, h, "centro", peak_opacity=170)
    bg = Image.alpha_composite(bg, gradient)

    draw = ImageDraw.Draw(bg)
    font_size = max(44, w // 11)
    font = _load_font(FONT_TITLE, font_size)

    # Texto entre nono 4 e nono 6
    _wrap_and_draw(draw, headline, font, w, nono * 3, nono * 6, shadow_offset=5)

    return _encode_b64(bg.convert("RGB"))


def _render_texto_posicao(bg_b64: str, headline: str, dims: dict, posicao: str) -> str:
    """Texto posicionado por nonos da imagem.

    Topo: nonos 2 a 4 (texto grande, visivel no celular)
    Embaixo: nonos 6 a 8 (mais pra cima que o rodape, legivel)
    """
    bg = _decode_b64(bg_b64).resize((dims["width"], dims["height"]), Image.LANCZOS)
    w, h = bg.size
    nono = h // 9

    # Gradiente suave cobrindo metade da imagem
    grad_h = h // 2
    gradient = _make_gradient_fast(w, grad_h, posicao, peak_opacity=180)
    full_grad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if posicao == "topo":
        full_grad.paste(gradient, (0, 0))
    else:
        full_grad.paste(gradient, (0, h - grad_h))
    bg = Image.alpha_composite(bg, full_grad)

    draw = ImageDraw.Draw(bg)
    font_size = max(44, w // 11)
    font = _load_font(FONT_TITLE, font_size)

    if posicao == "topo":
        # Nonos 2 a 4
        _wrap_and_draw(draw, headline, font, w, nono * 1, nono * 4, shadow_offset=5)
    else:
        # Nonos 6 a 8
        _wrap_and_draw(draw, headline, font, w, nono * 5, nono * 8, shadow_offset=5)

    return _encode_b64(bg.convert("RGB"))


def render_texto_no_topo(bg_b64: str, headline: str, dims: dict) -> str:
    return _render_texto_posicao(bg_b64, headline, dims, "topo")


def render_texto_embaixo(bg_b64: str, headline: str, dims: dict) -> str:
    return _render_texto_posicao(bg_b64, headline, dims, "baixo")


TEMPLATE_RENDERERS = {
    "texto_centralizado": render_texto_centralizado,
    "texto_no_topo": render_texto_no_topo,
    "texto_embaixo": render_texto_embaixo,
}


def render_upload(bg_b64: str, headline: str, template: str, formato: str = "post_unico") -> str | None:
    """Renderiza texto sobre fundo. Retorna base64 PNG ou None se template precisa de Gemini."""
    renderer = TEMPLATE_RENDERERS.get(template)
    if not renderer:
        return None  # Template com avatar ou criativo — precisa de Gemini

    from utils.dimensions import get_dims
    dims = get_dims(formato)
    return renderer(bg_b64, headline, dims)


def compositar_criativo(frame_b64: str, gemini_b64: str, formato: str = "post_unico") -> str:
    """Chroma key: remove fundo preto da imagem Gemini e compoe sobre o frame original.

    1. Abre frame original (intacto)
    2. Abre imagem Gemini (gerada em fundo preto)
    3. Calcula alpha a partir da luminosidade — preto = transparente, resto = visivel
    4. Cola por cima do frame
    """
    from utils.dimensions import get_dims
    dims = get_dims(formato)
    w, h = dims["width"], dims["height"]

    frame = _decode_b64(frame_b64).resize((w, h), Image.LANCZOS).convert("RGBA")
    arte = _decode_b64(gemini_b64).resize((w, h), Image.LANCZOS).convert("RGBA")

    # Extrair luminosidade de cada pixel pra criar mascara alpha
    # Preto puro (0,0,0) = totalmente transparente
    # Qualquer cor com brilho = visivel
    import numpy as np
    arr = np.array(arte, dtype=np.float32)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    # Luminosidade perceptual
    lum = 0.299 * r + 0.587 * g + 0.114 * b

    # Threshold: pixels muito escuros ficam transparentes
    # Curva suave pra transicao (evita bordas duras)
    THRESHOLD = 30  # abaixo disso = totalmente transparente
    SOFT_RANGE = 40  # faixa de transicao suave
    alpha = np.clip((lum - THRESHOLD) / SOFT_RANGE * 255, 0, 255).astype(np.uint8)

    # Aplicar alpha na imagem do Gemini
    arte_arr = np.array(arte)
    arte_arr[:, :, 3] = alpha
    arte_rgba = Image.fromarray(arte_arr, "RGBA")

    # Compositar: frame embaixo + arte por cima
    result = Image.alpha_composite(frame, arte_rgba)
    return _encode_b64(result.convert("RGB"))
