"""Sobrepoe a foto real na posicao definida pelo brand profile.

Posicao configuravel pelo usuario na tela de marcas.
Simples, confiavel, sem deteccao.
"""
import base64
import io

from PIL import Image, ImageDraw

AA = 4  # anti-alias multiplier


def overlay_foto(
    slide_b64: str,
    foto_b64: str,
    is_cta: bool = False,
    posicao: int = 1,
    total: int = 5,
    brand: dict | None = None,
) -> str:
    """Cola foto na posicao do brand profile."""
    if not foto_b64:
        return slide_b64

    slide = _decode(slide_b64)
    foto = _decode(foto_b64)
    w, h = slide.size
    canvas = slide.convert("RGBA")

    # Posicao do brand ou padrao
    foto_cfg = (brand or {}).get("foto", {})
    x_pct = foto_cfg.get("x_pct", 0.06)
    y_pct = foto_cfg.get("y_pct", 0.93)
    r_pct = foto_cfg.get("raio_pct", 0.03)
    borda_hex = foto_cfg.get("borda_cor", "#A78BFA")
    borda_cor = _hex_to_rgba(borda_hex)

    cx = int(w * x_pct)
    cy = int(h * y_pct)
    r = int(w * r_pct)

    canvas = _paste_circle(canvas, foto, cx, cy, r, borda_cor)

    buf = io.BytesIO()
    canvas.convert("RGB").save(buf, format="PNG", quality=95)
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"


def _paste_circle(
    canvas: Image.Image,
    foto: Image.Image,
    cx: int,
    cy: int,
    r: int,
    borda_cor: tuple = (167, 139, 250, 255),
) -> Image.Image:
    """Cola foto circular com borda colorida."""
    size = r * 2
    border = max(2, r // 10)

    big = size * AA
    border_big = border * AA

    foto_big = foto.resize((big, big), Image.LANCZOS)
    mask_big = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask_big).ellipse([0, 0, big - 1, big - 1], fill=255)
    circ = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    circ.paste(foto_big.convert("RGBA"), (0, 0), mask_big)

    total_big = big + border_big * 2
    with_border = Image.new("RGBA", (total_big, total_big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(with_border)
    draw.ellipse([0, 0, total_big - 1, total_big - 1], fill=borda_cor)
    with_border.paste(circ, (border_big, border_big), circ)

    final_size = size + border * 2
    with_border = with_border.resize((final_size, final_size), Image.LANCZOS)

    final_r = final_size // 2
    canvas.paste(with_border, (cx - final_r, cy - final_r), with_border)
    return canvas


def _hex_to_rgba(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    if len(h) == 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    return (167, 139, 250, 255)


def _decode(data_uri: str) -> Image.Image:
    if "," in data_uri:
        b64 = data_uri.split(",", 1)[1]
    else:
        b64 = data_uri
    return Image.open(io.BytesIO(base64.b64decode(b64)))
