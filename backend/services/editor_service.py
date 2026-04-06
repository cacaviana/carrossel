"""Service do editor — logica de negocio extraida do router config.py."""

import base64 as b64
import io
import json as _json
import os
from pathlib import Path

import httpx
from PIL import Image, ImageDraw


def salvar_pdf(slides_data: list, logo_data: str, borda_cor_hex: str | None = None) -> dict:
    """Recebe slides + logo + posicoes e gera PDF. Retorna {pdf_base64, total_slides}."""

    # Decodificar logo
    logo_raw = logo_data.split(",")[1] if "," in logo_data else logo_data
    logo_img = Image.open(io.BytesIO(b64.b64decode(logo_raw))).convert("RGBA")

    def _hex_rgba(hex_color):
        h = hex_color.lstrip("#")
        if len(h) == 6:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
        return (167, 139, 250, 255)

    pil_pages = []
    for s in slides_data:
        img_raw = s["image"].split(",")[1] if "," in s["image"] else s["image"]
        slide_img = Image.open(io.BytesIO(b64.b64decode(img_raw))).convert("RGBA")

        logo_size = int(s.get("logo_size", 60))
        logo_x = int(s.get("logo_x", 50))
        logo_y = int(s.get("logo_y", 1290))

        w, h = slide_img.size
        scale_x = w / 1080
        scale_y = h / 1350
        actual_size = int(logo_size * scale_x)
        actual_x = int(logo_x * scale_x)
        actual_y = int(logo_y * scale_y)

        # Logo circular
        logo_resized = logo_img.resize((actual_size, actual_size), Image.LANCZOS)
        mask = Image.new("L", (actual_size, actual_size), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, actual_size - 1, actual_size - 1], fill=255)
        circular = Image.new("RGBA", (actual_size, actual_size), (0, 0, 0, 0))
        circular.paste(logo_resized, (0, 0), mask)

        if borda_cor_hex:
            # Com borda anti-aliased + semi-transparente
            AA = 4
            border = max(2, actual_size // 20)
            total = actual_size + border * 2
            big = total * AA
            border_big = border * AA
            circ_big = circular.resize((actual_size * AA, actual_size * AA), Image.LANCZOS)
            with_border_big = Image.new("RGBA", (big, big), (0, 0, 0, 0))
            r, g, b_val, _ = _hex_rgba(borda_cor_hex)
            ImageDraw.Draw(with_border_big).ellipse([0, 0, big - 1, big - 1], fill=(r, g, b_val, 140))
            with_border_big.paste(circ_big, (border_big, border_big), circ_big)
            with_border = with_border_big.resize((total, total), Image.LANCZOS)
            paste_x = actual_x - total // 2
            paste_y = actual_y - total // 2
            slide_img.paste(with_border, (paste_x, paste_y), with_border)
        else:
            # Sem borda
            paste_x = actual_x - actual_size // 2
            paste_y = actual_y - actual_size // 2
            slide_img.paste(circular, (paste_x, paste_y), circular)

        page = slide_img.convert("RGB")
        if page.size != (1080, 1350):
            page = page.resize((1080, 1350), Image.LANCZOS)
        pil_pages.append(page)

    # Gerar PDF
    buf = io.BytesIO()
    pil_pages[0].save(buf, "PDF", save_all=True, append_images=pil_pages[1:], resolution=150)
    pdf_b64 = b64.b64encode(buf.getvalue()).decode()

    return {"pdf_base64": pdf_b64, "total_slides": len(pil_pages)}


def buscar_slides_limpos(brand: str) -> dict | None:
    """Lê JSON de slides limpos do disco. Retorna None se não encontrado."""
    path = Path(__file__).parent.parent / f"{brand}_slides.json"
    if not path.exists():
        return None
    return _json.loads(path.read_text(encoding="utf-8"))


async def corrigir_texto(image: str, slide: dict) -> dict | None:
    """Tenta corrigir texto ate 3x preservando visual. Usa utils/image_text_fixer (DRY)."""
    from utils.image_text_fixer import corrigir_texto_na_imagem

    api_key = os.getenv("GEMINI_API_KEY", "")

    titulo = slide.get("headline") or slide.get("title", "")
    corpo = ""
    bullets = slide.get("bullets", [])
    if bullets:
        corpo = "\n".join(bullets)
    elif slide.get("subline"):
        corpo = slide["subline"]

    async with httpx.AsyncClient(timeout=120.0) as client:
        result = await corrigir_texto_na_imagem(
            client=client,
            image_b64=image,
            titulo=titulo,
            corpo=corpo,
            api_key=api_key,
            max_tentativas=3,
        )

    if result["image"] is None:
        return None

    response = {
        "image": result["image"],
        "tentativas": result["tentativas"],
        "texto_lido": result["texto_lido"],
    }
    if not result["corrigido"]:
        response["aviso"] = "Texto pode nao estar 100% correto"
    return response
