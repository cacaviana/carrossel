"""Geracao inteligente de imagens: Gemini faz arte, HTML/CSS garante texto.

Fluxo por slide:
1. Gemini gera imagem completa (com texto) — otimista
2. Visao valida se texto esta correto
3. Se correto → usa direto
4. Se errado → Gemini gera fundo limpo (sem texto) + Playwright renderiza texto via HTML/CSS
5. Overlay foto via posicao fixa
"""
import asyncio
import os

import httpx

from factories.imagem_factory import build_payload
from mappers.imagem_mapper import extract_image_from_response
from services.foto_overlay import overlay_foto
from services.text_validator import validar_texto_slide
from services.slide_renderer import gerar_slides_com_texto_exato
from services.brand_prompt_builder import carregar_brand

from utils.constants import GEMINI_API_URL as API_URL


MAX_CONCURRENT_SLIDES = 3  # Gemini rate limit safe

NANO_BANANA_MODEL = "gemini-2.5-flash-image"

# Face safe zone (em %) — box central que sempre fica preto no overlay
FACE_BOX_TOP = 0.22
FACE_BOX_BOTTOM = 0.62
FACE_BOX_LEFT = 0.18
FACE_BOX_RIGHT = 0.82
FACE_FEATHER_PX = 40


def _mascarar_face_zone(banner_b64: str, dims: dict) -> str:
    """Pinta preto (com feather suave) na caixa central do banner.

    Garante que na hora do chroma-key a area do rosto fique transparente,
    mostrando a foto original por baixo. Feather evita borda dura retangular.
    """
    import base64
    import io
    from PIL import Image, ImageDraw, ImageFilter

    raw = banner_b64.split(",", 1)[1] if "," in banner_b64 else banner_b64
    img = Image.open(io.BytesIO(base64.b64decode(raw))).convert("RGB")
    w_target, h_target = dims["width"], dims["height"]
    img = img.resize((w_target, h_target), Image.LANCZOS)

    # Mascara branca onde queremos pintar preto (dentro do box)
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    x0 = int(w_target * FACE_BOX_LEFT)
    y0 = int(h_target * FACE_BOX_TOP)
    x1 = int(w_target * FACE_BOX_RIGHT)
    y1 = int(h_target * FACE_BOX_BOTTOM)
    draw.rectangle([x0, y0, x1, y1], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=FACE_FEATHER_PX))

    preto = Image.new("RGB", img.size, (0, 0, 0))
    img = Image.composite(preto, img, mask)

    buf = io.BytesIO()
    img.save(buf, "PNG")
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"


def _gemini_aspect_for_format(formato: str) -> str:
    from utils.dimensions import get_dims
    dims = get_dims(formato)
    ratio = dims["ratio"]
    if ratio in ("9:16", "4:5", "1:1", "16:9"):
        return ratio
    return "4:5"


DEFAULT_BANNER_DESCRICAO = (
    "A rich editorial translucent banner (55-70% opacity) with soft gradient fills, "
    "subtle decorative motifs, flowing curves, glowing dots and particles, and light rays. "
    "Layered cinematic depth, magazine-style editorial vibe — multiple translucent elements "
    "stacked. Keep motifs GENERIC (no specific themed shapes) — the brand should define its "
    "own banner style via dna.banner."
)


async def _gerar_criativo_flash_plus_pillow(
    client: httpx.AsyncClient,
    headline: str,
    background_b64: str,
    gemini_key: str,
    formato: str,
    cor_hero: str,
    posicao: str = "topo",
    banner_descricao: str | None = None,
) -> str | None:
    """Criativo: Gemini Flash recebe a foto e adiciona UM banner rico.
    Pillow adiciona o texto em cima.

    posicao: "topo" ou "baixo" — onde colocar o banner
    banner_descricao: descricao do estilo do banner (vem do brand.dna.banner).
                      Se None, usa DEFAULT_BANNER_DESCRICAO.
    """
    bg_raw = background_b64.split(",", 1)[1] if "," in background_b64 else background_b64

    pos_label = "BOTTOM" if posicao == "baixo" else "TOP"
    pos_range = "bottom 20-25%" if posicao == "baixo" else "top 20-25%"
    pos_neighbor = "below the person" if posicao == "baixo" else "above the person's head"
    descricao = banner_descricao or DEFAULT_BANNER_DESCRICAO

    prompt = (
        "[PRIMARY TASK - RICH EDITORIAL BANNER OVER PRESERVED PHOTO]\n"
        "\n"
        "Use the provided image as the base and preserve it EXACTLY.\n"
        "\n"
        "---\n"
        "\n"
        "PRESERVE (CRITICAL - DO NOT VIOLATE):\n"
        "- The person's face, expression, pose, body, clothing, hands — keep 100% identical to the original\n"
        "- The background setting — keep identical\n"
        "- Do NOT re-render or re-synthesize any facial feature\n"
        "- Do NOT zoom, do NOT crop\n"
        "\n"
        "---\n"
        "\n"
        f"ADD ONE BANNER at the {pos_label} of the image ({pos_neighbor}, not covering the body or face):\n"
        "\n"
        "BANNER SPEC (from brand identity):\n"
        f"- Color base: {cor_hero}\n"
        f"- Style: {descricao}\n"
        f"- Position: {pos_range} of the image\n"
        "- Shape: wide horizontal or slightly diagonal band\n"
        "\n"
        "---\n"
        "\n"
        "STRICTLY FORBIDDEN:\n"
        "- NO flat solid opaque color block\n"
        "- NO UI-like rectangle (rounded corners, shadows, button style)\n"
        "- NO glassmorphism / blur\n"
        "- The banner must NOT cover the person's face or body\n"
        "- Do NOT add text, letters, words, numbers\n"
        "\n"
        "GOAL:\n"
        f"The original photo with a rich, translucent editorial banner at the {pos_label}."
    )

    payload = {
        "contents": [{
            "parts": [
                {"inline_data": {"mime_type": "image/png", "data": bg_raw}},
                {"text": prompt},
            ],
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "temperature": 0.6,
            "imageConfig": {"aspectRatio": _gemini_aspect_for_format(formato)},
        },
    }

    res = await client.post(
        API_URL.format(model=NANO_BANANA_MODEL),
        json=payload,
        headers={"x-goog-api-key": gemini_key},
        timeout=180.0,
    )
    res.raise_for_status()
    img_com_banner = extract_image_from_response(res.json())
    if not img_com_banner:
        return None

    from services.upload_text_overlay import render_texto_sobre_banner
    from utils.dimensions import get_dims
    dims = get_dims(formato)
    final_b64 = render_texto_sobre_banner(img_com_banner, headline, dims, posicao=posicao)
    return f"data:image/png;base64,{final_b64}"


async def gerar_imagens_smart(
    slides: list[dict],
    gemini_api_key: str,
    foto_criador: str | None = None,
    brand_slug: str | None = None,
    avatar_mode: str = "livre",
    formato: str = "carrossel",
    skip_validation: bool = False,
    pipeline_id: str | None = None,
    background_b64: str | None = None,
) -> list[str | None]:
    """Gera imagens com fallback inteligente pra texto errado.

    Usa asyncio.gather com semaforo para paralelizar chamadas ao Gemini,
    limitando a MAX_CONCURRENT_SLIDES simultaneas pra respeitar rate limit.

    Args:
        pipeline_id: ID do pipeline (usado como seed pra refs_selector).
                     Garante que todos os slides do mesmo carrossel usem
                     as mesmas REF1/REF2 fixas (Fase 3).
    """
    if not gemini_api_key:
        gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    brand = carregar_brand(brand_slug) if brand_slug else None
    total = len(slides)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_SLIDES)

    # REGRA DE OURO (Fase 3): sortear REF1/REF2 UMA VEZ por carrossel
    refs_fixas = None
    if brand_slug:
        from factories.refs_selector import escolher_refs_fixas
        seed = pipeline_id or f"default-{brand_slug}"
        refs_fixas = escolher_refs_fixas(brand_slug, seed)

    async def process_slide(i: int, slide: dict) -> tuple[int, str | None]:
        async with semaphore:
            position = i + 1
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    img = await _gerar_slide_smart(
                        client, slide, position, total,
                        gemini_api_key, foto_criador, brand_slug, brand,
                        avatar_mode=avatar_mode,
                        formato=formato,
                        skip_validation=skip_validation,
                        refs_fixas=refs_fixas,
                        background_b64=background_b64,
                    )
                return (i, img)
            except Exception as e:
                try:
                    print(f"Erro no slide {position}: {e}")
                except UnicodeEncodeError:
                    print(f"Erro no slide {position}")
                return (i, None)

    tasks = [process_slide(i, slide) for i, slide in enumerate(slides)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Montar lista ordenada por indice
    images: list[str | None] = [None] * total
    for result in results:
        if isinstance(result, Exception):
            continue
        idx, img = result
        images[idx] = img

    return images


async def _gerar_slide_smart(
    client: httpx.AsyncClient,
    slide: dict,
    position: int,
    total: int,
    api_key: str,
    foto_criador: str | None,
    brand_slug: str | None,
    brand: dict | None,
    avatar_mode: str = "livre",
    formato: str = "carrossel",
    skip_validation: bool = False,
    refs_fixas: dict | None = None,
    background_b64: str | None = None,
) -> str | None:
    """Gera 1 slide com validacao e fallback."""

    # Modo criativo upload: Gemini Flash (nano banana) faz foto+banner, Pillow poe texto
    illustration = slide.get("illustration_description", "")
    is_criativo_upload = bool(background_b64) and (
        "creative visual elements" in illustration.lower() or "layers" in illustration.lower()
    )
    if is_criativo_upload:
        try:
            headline = slide.get("headline") or slide.get("title", "") or ""
            cor_hero = "#A78BFA"
            banner_descricao = None
            if brand:
                cores_map = brand.get("cores", {}) or {}
                cor_hero = cores_map.get("acento_principal") or cores_map.get("primaria") or "#A78BFA"
                dna = brand.get("dna", {}) or {}
                banner_descricao = dna.get("banner") or None

            # Posicao: detectar no illustration_description ("BOTTOM area" -> baixo)
            posicao_banner = "baixo" if "bottom area" in illustration.lower() else "topo"

            img = await _gerar_criativo_flash_plus_pillow(
                client, headline, background_b64, api_key, formato, cor_hero,
                posicao=posicao_banner, banner_descricao=banner_descricao,
            )
            if img:
                if foto_criador:
                    is_cta = slide.get("type") == "cta"
                    img = overlay_foto(img, foto_criador, is_cta=is_cta, posicao=position, total=total)
                print(f"  Slide {position}: criativo {posicao_banner} via Flash+Pillow")
                return img
        except Exception as e:
            print(f"  Slide {position}: Flash+Pillow falhou ({e}), fallback Gemini Pro")

    # Passo 1: Gemini gera imagem completa (otimista) — retry se ratio errado
    from utils.dimensions import get_dims
    dims = get_dims(formato)
    target_ratio = dims["width"] / dims["height"]
    MAX_RATIO_RETRIES = 2

    img_completa = None
    for attempt in range(1, MAX_RATIO_RETRIES + 2):
        model, payload = build_payload(slide, position, total, brand_slug=brand_slug, avatar_mode=avatar_mode, formato=formato, refs_fixas=refs_fixas, background_b64=background_b64)
        res = await client.post(
            API_URL.format(model=model),
            json=payload,
            headers={"x-goog-api-key": api_key},
        )
        res.raise_for_status()
        img_completa = extract_image_from_response(res.json())

        if not img_completa:
            break

        # Validar aspect ratio
        try:
            import base64
            from io import BytesIO
            from PIL import Image
            raw = img_completa.split(",", 1)[1] if "," in img_completa else img_completa
            img_check = Image.open(BytesIO(base64.b64decode(raw)))
            img_ratio = img_check.width / img_check.height
            if abs(img_ratio - target_ratio) < 0.1:
                break  # ratio correto
            print(f"  Slide {position}: ratio errado ({img_check.width}x{img_check.height} = {img_ratio:.2f}, esperado {target_ratio:.2f}) — tentativa {attempt}/{MAX_RATIO_RETRIES + 1}")
        except Exception:
            break  # se nao conseguir verificar, aceita

        if attempt > MAX_RATIO_RETRIES:
            print(f"  Slide {position}: aceitando imagem apos {MAX_RATIO_RETRIES + 1} tentativas")

    if not img_completa:
        return None

    # Se skip_validation (regenerar do editor), retornar direto sem corrigir
    if skip_validation:
        return img_completa

    # Passo 2: Validar texto
    validacao = await validar_texto_slide(img_completa, slide, api_key)

    if validacao.get("valido", True):
        return img_completa

    # Passo 3: Texto errado — corrigir preservando o visual (mesma imagem, so muda texto)
    from utils.image_text_fixer import corrigir_texto_na_imagem
    from utils.slide_text_extractor import extrair_texto_slide

    titulo, corpo = extrair_texto_slide(slide)

    try:
        print(f"  Slide {position}: texto errado, corrigindo preservando visual...")
    except UnicodeEncodeError:
        pass

    result = await corrigir_texto_na_imagem(
        client=client,
        image_b64=img_completa,
        titulo=titulo,
        corpo=corpo,
        api_key=api_key,
        max_tentativas=2,
        modelo="gemini-3-pro-image-preview",
    )

    if result["corrigido"]:
        try:
            print(f"  Slide {position}: texto corrigido na tentativa {result['tentativas']}!")
        except UnicodeEncodeError:
            pass
        return result["image"]

    try:
        print(f"  Slide {position}: texto nao ficou 100%, usando melhor tentativa")
    except UnicodeEncodeError:
        pass
    return result["image"]


def _build_bg_only_prompt(slide: dict, position: int, total: int, brand_slug: str | None, formato: str = "carrossel") -> str:
    """Prompt pra gerar APENAS o fundo, sem texto."""
    from services.brand_prompt_builder import carregar_brand, build_design_system_text
    from utils.dimensions import get_prompt_size_str

    brand = carregar_brand(brand_slug) if brand_slug else None
    if brand:
        ds = build_design_system_text(brand)
    else:
        ds = "Professional background. Premium style."

    size_str = get_prompt_size_str(formato)

    return (
        f"Generate a background image for a social media slide ({size_str}). "
        f"CRITICAL: NO TEXT whatsoever. No letters, no words, no numbers. "
        f"This is ONLY a background/atmosphere image with decorative elements. "
        f"{ds} "
        f"Beautiful, premium, professional background. No text."
    )


def _default_brand() -> dict:
    """Carrega o primeiro brand disponivel como fallback."""
    from services.brand_prompt_builder import listar_brands as _listar
    brands = _listar()
    if brands:
        b = carregar_brand(brands[0]["slug"])
        if b:
            return b
    return {"cores": {}, "fontes": {}, "elementos": {}, "visual": {}}
