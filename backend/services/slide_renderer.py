"""Renderiza slides com fundo Gemini + texto HTML/CSS via Playwright.

Gemini gera APENAS o fundo (sem texto).
Playwright renderiza o texto perfeito por cima.
Resultado: visual bonito + texto 100% correto.
"""
import asyncio
import base64
import io
import os
from pathlib import Path

import httpx

from mappers.imagem_mapper import extract_image_from_response
from services.brand_prompt_builder import carregar_brand, build_design_system_text
from utils.dimensions import get_dims, get_prompt_size_str

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
from utils.constants import GEMINI_API_URL as API_URL


async def gerar_slides_com_texto_exato(
    slides: list[dict],
    brand_slug: str = "",
    gemini_api_key: str = "",
    formato: str = "carrossel",
) -> list[str | None]:
    """Gera slides com texto garantido.

    1. Gemini gera fundo bonito (SEM texto)
    2. Playwright renderiza HTML com texto exato + fundo
    """
    if not gemini_api_key:
        gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    brand = carregar_brand(brand_slug) or _default_brand()
    total = len(slides)
    dims = get_dims(formato)
    results: list[str | None] = []

    async with httpx.AsyncClient(timeout=120.0) as client:
        for i, slide in enumerate(slides):
            try:
                # 1. Gerar fundo bonito sem texto
                bg = await _gerar_fundo(client, slide, i + 1, total, brand, gemini_api_key, formato=formato)

                # 2. Renderizar texto por cima via HTML/CSS
                html = _build_slide_html(slide, i + 1, total, brand, bg, formato=formato)
                img_b64 = await _screenshot(html, dims["width"], dims["height"])
                results.append(img_b64)

                try:
                    print(f"  Slide {i+1}: OK")
                except UnicodeEncodeError:
                    pass
            except Exception as e:
                try:
                    print(f"  Slide {i+1}: erro - {e}")
                except UnicodeEncodeError:
                    pass
                results.append(None)

            if i < total - 1:
                await asyncio.sleep(2)

    return results


async def _gerar_fundo(client, slide, position, total, brand, api_key, formato: str = "carrossel"):
    """Gemini gera apenas o fundo/arte, sem texto nenhum."""
    visual = brand.get("visual", {})
    cores = brand.get("cores", {})
    size_str = get_prompt_size_str(formato)

    prompt = (
        f"Generate a beautiful background image for a slide ({size_str}). "
        f"CRITICAL: absolutely NO TEXT, NO LETTERS, NO WORDS, NO NUMBERS anywhere in the image. "
        f"This is ONLY a decorative background. "
        f"{visual.get('estilo_fundo', 'Dark gradient background.')} "
        f"{visual.get('estilo_desenho', '')} "
        f"Main color: {cores.get('acento_principal', '')}. "
        f"Background: {cores.get('fundo', '')}. "
        f"Style: premium, professional, atmospheric. "
        f"NO text. NO letters. Pure visual art only."
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
    }

    res = await client.post(
        API_URL.format(model="gemini-2.5-flash-image"),
        json=payload,
        headers={"x-goog-api-key": api_key},
    )
    res.raise_for_status()
    return extract_image_from_response(res.json())


def _build_slide_html(slide, position, total, brand, bg_b64=None, formato: str = "carrossel"):
    """Monta HTML bonito com fundo Gemini e texto exato."""
    dims = get_dims(formato)
    slide_w = dims["width"]
    slide_h = dims["height"]
    cores = brand.get("cores", {})
    fontes = brand.get("fontes", {})
    elementos = brand.get("elementos", {})
    visual = brand.get("visual", {})
    slide_type = slide.get("type", "content")

    bg_css = ""
    if bg_b64:
        raw = bg_b64.split(",")[1] if "," in bg_b64 else bg_b64
        bg_css = f"background-image: url('data:image/png;base64,{raw}'); background-size: cover; background-position: center;"

    fundo = cores.get("fundo", "#111111")
    principal = cores.get("acento_principal", "#888888")
    secundario = cores.get("acento_secundario", "#888888")
    texto_cor = cores.get("texto_principal", "#FFFFFF")
    texto_sec = cores.get("texto_secundario", "#9896A3")
    card_bg = cores.get("card", "rgba(18,18,26,0.75)")
    card_borda = cores.get("card_borda", "rgba(167,139,250,0.2)")
    fonte = fontes.get("titulo", "sans-serif")

    # Conteudo baseado no tipo
    if slide_type == "cover":
        content = _html_cover(slide, elementos, principal, texto_cor, texto_sec, secundario)
    elif slide_type == "cta":
        content = _html_cta(slide, elementos, principal, texto_cor, texto_sec, position, total)
    else:
        content = _html_content(slide, principal, texto_cor, texto_sec, card_bg, card_borda, elementos, position, total)

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family={fonte.replace(' ','+')}:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:{slide_w}px; height:{slide_h}px; overflow:hidden; font-family:'{fonte}',sans-serif; background:{fundo}; color:{texto_cor}; }}
.slide {{ width:{slide_w}px; height:{slide_h}px; position:relative; display:flex; flex-direction:column; {bg_css} }}
.overlay {{ position:absolute; inset:0; background:rgba(0,0,0,0.15); }}
.content {{ position:relative; z-index:1; flex:1; display:flex; flex-direction:column; padding:60px 56px; }}
.badge {{ display:inline-flex; align-self:flex-start; padding:10px 28px; border-radius:9999px; font-size:16px; font-weight:600; letter-spacing:0.5px; text-transform:uppercase; margin-bottom:28px; background:rgba({_hex_rgb(principal)},0.15); color:{principal}; border:1px solid rgba({_hex_rgb(principal)},0.3); backdrop-filter:blur(8px); }}
.headline {{ font-size:64px; font-weight:700; line-height:1.08; margin-bottom:20px; text-shadow:0 2px 20px rgba(0,0,0,0.5); }}
.headline .kw {{ color:{principal}; }}
.subline {{ font-size:26px; font-weight:300; line-height:1.4; color:{texto_sec}; text-shadow:0 1px 10px rgba(0,0,0,0.5); }}
.card {{ background:{card_bg}; border:1px solid {card_borda}; border-radius:20px; padding:44px; backdrop-filter:blur(24px); -webkit-backdrop-filter:blur(24px); box-shadow:0 8px 32px rgba(0,0,0,0.3); }}
.card-title {{ font-size:44px; font-weight:700; line-height:1.12; margin-bottom:24px; text-shadow:0 1px 8px rgba(0,0,0,0.3); }}
.bullets {{ list-style:none; display:flex; flex-direction:column; gap:18px; }}
.bullets li {{ font-size:24px; line-height:1.45; color:{texto_sec}; padding-left:24px; position:relative; }}
.bullets li::before {{ content:'\\2192'; position:absolute; left:0; color:{principal}; font-weight:600; }}
.footer {{ margin-top:auto; display:flex; align-items:center; gap:14px; padding-top:20px; }}
.footer-name {{ font-size:18px; font-weight:500; text-shadow:0 1px 6px rgba(0,0,0,0.5); }}
.footer-counter {{ margin-left:auto; font-size:16px; color:{texto_sec}; font-family:monospace; }}
</style></head>
<body><div class="slide"><div class="overlay"></div><div class="content">
{content}
</div></div></body></html>"""


def _html_cover(slide, elementos, principal, texto_cor, texto_sec, secundario):
    headline = slide.get("headline", "")
    subline = slide.get("subline", "")
    badge = elementos.get("badge_topo", "")
    return f"""
<div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
  <div class="badge" style="background:rgba({_hex_rgb(secundario)},0.15);color:{secundario};border-color:rgba({_hex_rgb(secundario)},0.3);">{badge}</div>
  <div class="headline">{headline}</div>
  <div class="subline">{subline}</div>
</div>
<div class="footer">
  <span class="footer-name">{elementos.get('rodape_nome','')}</span>
  <span class="footer-counter">1/N</span>
</div>"""


def _html_content(slide, principal, texto_cor, texto_sec, card_bg, card_borda, elementos, pos, total):
    title = slide.get("title", "")
    etapa = slide.get("etapa", "")
    bullets = slide.get("bullets", [])
    bullets_html = "".join(f"<li>{b}</li>" for b in bullets)
    badge_html = f'<div class="badge">{etapa}</div>' if etapa else ""
    return f"""
<div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
  <div class="card">
    {badge_html}
    <div class="card-title">{title}</div>
    <ul class="bullets">{bullets_html}</ul>
  </div>
</div>
<div class="footer">
  <span class="footer-name">{elementos.get('rodape_nome','')}</span>
  <span class="footer-counter">{pos}/{total}</span>
</div>"""


def _html_cta(slide, elementos, principal, texto_cor, texto_sec, pos, total):
    headline = slide.get("headline", "")
    subline = slide.get("subline", "")
    tags = slide.get("tags", [])
    tags_html = "".join(f'<span style="padding:10px 24px;border-radius:9999px;font-size:16px;background:rgba({_hex_rgb(principal)},0.12);color:{principal};border:1px solid rgba({_hex_rgb(principal)},0.25);">{t}</span>' for t in tags)
    return f"""
<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;">
  <div class="headline" style="font-size:56px;">{headline}</div>
  <div class="subline" style="text-align:center;margin-bottom:24px;">{subline}</div>
  <div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center;">{tags_html}</div>
</div>
<div class="footer" style="justify-content:center;">
  <span class="footer-name" style="font-size:16px;color:{texto_sec};">{elementos.get('rodape_nome','')} &mdash; {elementos.get('rodape_instituicao','')} &mdash; {elementos.get('rodape_extra','')}</span>
</div>"""


def _hex_rgb(hex_color):
    h = hex_color.lstrip("#")
    if len(h) == 6:
        return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"
    return "167,139,250"


async def _screenshot(html: str, width: int = 1080, height: int = 1350) -> str:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height})
        await page.set_content(html)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        screenshot = await page.screenshot(type="png")
        await browser.close()
    return f"data:image/png;base64,{base64.b64encode(screenshot).decode()}"


def _default_brand():
    """Carrega o primeiro brand disponivel."""
    from services.brand_prompt_builder import listar_brands, carregar_brand as _load
    brands = listar_brands()
    if brands:
        b = _load(brands[0]["slug"])
        if b:
            return b
    return {"cores": {}, "fontes": {}, "elementos": {}, "visual": {}}
