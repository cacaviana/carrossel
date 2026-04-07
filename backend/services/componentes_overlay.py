"""Componentes visuais fixos renderizados via Pillow.

Garante consistencia pixel-perfect em:
- Badge "Carlos Viana" (pill verde no topo)
- Rodape (foto circular + nome + contador/DESLIZA)
- Foto grande centralizada no CTA

A Gemini gera SEM esses elementos. Este modulo cola por cima.
"""
import base64
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"

# Cores
GREEN = (52, 211, 153)        # #34D399
PURPLE = (167, 139, 250)      # #A78BFA
WHITE = (255, 255, 255)
MUTED = (152, 150, 163)       # #9896A3
DARK = (10, 10, 15)
BADGE_BG = (52, 211, 153, 30) # verde com transparencia

AA = 4  # anti-aliasing multiplier


def aplicar_componentes(
    slide_b64: str,
    foto_b64: str | None,
    nome: str = "Carlos Viana",
    posicao: int = 1,
    total: int = 5,
    is_cta: bool = False,
) -> str:
    """Aplica todos os componentes fixos sobre o slide."""
    slide = _decode(slide_b64)
    foto = _decode(foto_b64) if foto_b64 else None
    w, h = slide.size
    scale = w / 1080

    canvas = slide.convert("RGBA")

    # 1. Badge "Carlos Viana" no topo
    canvas = _draw_badge(canvas, nome, scale)

    # 2. Rodape (foto + nome + contador)
    canvas = _draw_footer(canvas, foto, nome, posicao, total, scale)

    # 3. Foto grande centralizada no CTA
    if is_cta and foto:
        canvas = _draw_cta_photo(canvas, foto, scale)

    buf = io.BytesIO()
    canvas.convert("RGB").save(buf, format="PNG", quality=95)
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"


def _draw_badge(canvas: Image.Image, nome: str, scale: float) -> Image.Image:
    """Badge pill verde no topo do slide."""
    w, h = canvas.size
    draw = ImageDraw.Draw(canvas)

    font_size = int(12 * scale)
    font = _font("Outfit-SemiBold.ttf", font_size)
    bbox = draw.textbbox((0, 0), nome, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    pad_x = int(16 * scale)
    pad_y = int(6 * scale)
    pill_w = tw + pad_x * 2
    pill_h = th + pad_y * 2
    x = (w - pill_w) // 2
    y = int(32 * scale)

    # Pill com fundo semitransparente verde + borda
    pill = Image.new("RGBA", (pill_w * AA, pill_h * AA), (0, 0, 0, 0))
    d = ImageDraw.Draw(pill)
    r = pill_h * AA // 2
    d.rounded_rectangle([0, 0, pill_w * AA - 1, pill_h * AA - 1], radius=r,
                         fill=(52, 211, 153, 40), outline=(52, 211, 153, 200), width=AA)
    pill = pill.resize((pill_w, pill_h), Image.LANCZOS)

    canvas.paste(pill, (x, y), pill)

    # Texto
    tx = x + pad_x
    ty = y + pad_y - int(2 * scale)
    draw.text((tx, ty), nome, fill=GREEN, font=font)

    return canvas


def _draw_footer(canvas: Image.Image, foto: Image.Image | None, nome: str,
                 posicao: int, total: int, scale: float) -> Image.Image:
    """Rodape com foto circular + nome + contador."""
    w, h = canvas.size
    draw = ImageDraw.Draw(canvas)

    footer_h = int(64 * scale)
    y_base = h - footer_h
    margin = int(28 * scale)
    circle_size = int(36 * scale)

    # Fundo semitransparente pro rodape
    strip = Image.new("RGBA", (w, footer_h), (10, 10, 15, 160))
    canvas.paste(strip, (0, y_base), strip)

    # Foto circular
    if foto:
        foto_circle = _make_circle(foto, circle_size)
        fx = margin
        fy = y_base + (footer_h - circle_size) // 2
        canvas.paste(foto_circle, (fx, fy), foto_circle)
        text_x = fx + circle_size + int(10 * scale)
    else:
        text_x = margin

    # Nome
    font_name = _font("Outfit-SemiBold.ttf", int(13 * scale))
    name_y = y_base + (footer_h // 2) - int(8 * scale)
    draw.text((text_x, name_y), nome, fill=WHITE, font=font_name)

    # Contador ou DESLIZA
    if posicao == 1 and total > 1:
        right_text = "DESLIZA \u2192"
        right_color = PURPLE
    else:
        right_text = f"{posicao}/{total}"
        right_color = MUTED

    font_right = _font("Outfit-SemiBold.ttf", int(12 * scale))
    bbox = draw.textbbox((0, 0), right_text, font=font_right)
    rw = bbox[2] - bbox[0]
    rx = w - margin - rw
    ry = y_base + (footer_h // 2) - int(7 * scale)
    draw.text((rx, ry), right_text, fill=right_color, font=font_right)

    return canvas


def _draw_cta_photo(canvas: Image.Image, foto: Image.Image, scale: float) -> Image.Image:
    """Foto grande centralizada com borda roxa pro CTA."""
    w, h = canvas.size
    size = int(140 * scale)
    border = int(4 * scale)

    # Foto circular com borda roxa
    total_size = size + border * 2
    circle = Image.new("RGBA", (total_size * AA, total_size * AA), (0, 0, 0, 0))
    d = ImageDraw.Draw(circle)
    d.ellipse([0, 0, total_size * AA - 1, total_size * AA - 1], fill=(*PURPLE, 255))

    foto_big = foto.resize((size * AA, size * AA), Image.LANCZOS)
    mask = Image.new("L", (size * AA, size * AA), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size * AA - 1, size * AA - 1], fill=255)
    circle.paste(foto_big.convert("RGBA"), (border * AA, border * AA), mask)

    circle = circle.resize((total_size, total_size), Image.LANCZOS)

    # Centralizado, no terco superior
    cx = (w - total_size) // 2
    cy = int(h * 0.12)
    canvas.paste(circle, (cx, cy), circle)

    return canvas


def _make_circle(foto: Image.Image, size: int) -> Image.Image:
    """Cria foto circular com borda roxa fina."""
    border = max(2, size // 12)
    total = size + border * 2

    # Alta res pra anti-alias
    big = total * AA
    circle = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(circle)
    d.ellipse([0, 0, big - 1, big - 1], fill=(*PURPLE, 255))

    foto_big = foto.resize((size * AA, size * AA), Image.LANCZOS)
    mask = Image.new("L", (size * AA, size * AA), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size * AA - 1, size * AA - 1], fill=255)
    circle.paste(foto_big.convert("RGBA"), (border * AA, border * AA), mask)

    return circle.resize((total, total), Image.LANCZOS)


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONTS_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _decode(data_uri: str) -> Image.Image:
    if "," in data_uri:
        b64 = data_uri.split(",", 1)[1]
    else:
        b64 = data_uri
    return Image.open(io.BytesIO(base64.b64decode(b64)))
