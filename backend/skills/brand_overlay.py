from PIL import Image, ImageDraw
import io
import base64


def aplicar(image_base64: str, foto_criador_base64: str | None = None, logo_base64: str | None = None) -> str:
    """Aplica foto redonda do criador + logo da marca sobre a imagem.

    Retorna: image_base64 com overlay aplicado.
    """
    img_data = image_base64.split(",")[1] if "," in image_base64 else image_base64
    img = Image.open(io.BytesIO(base64.b64decode(img_data))).convert("RGBA")

    if foto_criador_base64:
        foto_data = foto_criador_base64.split(",")[1] if "," in foto_criador_base64 else foto_criador_base64
        foto = Image.open(io.BytesIO(base64.b64decode(foto_data))).convert("RGBA")
        foto = _make_circle(foto, size=80)
        # Posicao: canto inferior esquerdo com margem
        pos = (20, img.height - 100)
        img.paste(foto, pos, foto)

    if logo_base64:
        logo_data = logo_base64.split(",")[1] if "," in logo_base64 else logo_base64
        logo = Image.open(io.BytesIO(base64.b64decode(logo_data))).convert("RGBA")
        logo.thumbnail((120, 40))
        # Posicao: canto inferior direito com margem
        pos = (img.width - logo.width - 20, img.height - 60)
        img.paste(logo, pos, logo)

    # Converter de volta para base64
    buffer = io.BytesIO()
    img_rgb = img.convert("RGB")
    img_rgb.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def _make_circle(img: Image.Image, size: int) -> Image.Image:
    img = img.resize((size, size))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output.paste(img, (0, 0), mask)
    return output
