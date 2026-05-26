from PIL import Image, ImageDraw
import io
import base64


def aplicar(
    image_base64: str,
    foto_criador_base64: str | None = None,
    logo_base64: str | None = None,
    dimensao_id: str | None = None,  # legado (ignorado); mantido pra compat de chamadas
    modo: str | None = None,         # legado (ignorado)
) -> str:
    """Aplica overlay de marca sobre a imagem.

    Padrao: foto redonda (canto inferior esquerdo) + logo (canto inferior direito).
    Pos-pivot 2026-04-23: removidos os modos especiais por dimensao (anuncio
    agora usa o mesmo overlay do post_unico).

    Retorna: data URL da imagem final.
    """
    img_data = image_base64.split(",")[1] if "," in image_base64 else image_base64
    img = Image.open(io.BytesIO(base64.b64decode(img_data))).convert("RGBA")

    if foto_criador_base64:
        foto_data = foto_criador_base64.split(",")[1] if "," in foto_criador_base64 else foto_criador_base64
        foto = Image.open(io.BytesIO(base64.b64decode(foto_data))).convert("RGBA")
        foto = _make_circle(foto, size=80)
        pos = (20, img.height - 100)
        img.paste(foto, pos, foto)

    if logo_base64:
        logo_data = logo_base64.split(",")[1] if "," in logo_base64 else logo_base64
        logo = Image.open(io.BytesIO(base64.b64decode(logo_data))).convert("RGBA")
        logo.thumbnail((120, 40))
        pos = (img.width - logo.width - 10, img.height - logo.height - 10)
        img.paste(logo, pos, logo)

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
