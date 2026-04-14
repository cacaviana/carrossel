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


async def gerar_imagens_smart(
    slides: list[dict],
    gemini_api_key: str,
    foto_criador: str | None = None,
    brand_slug: str | None = None,
    avatar_mode: str = "livre",
    formato: str = "carrossel",
    skip_validation: bool = False,
    pipeline_id: str | None = None,
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
) -> str | None:
    """Gera 1 slide com validacao e fallback."""

    # Passo 1: Gemini gera imagem completa (otimista) — retry se ratio errado
    from utils.dimensions import get_dims
    dims = get_dims(formato)
    target_ratio = dims["width"] / dims["height"]
    MAX_RATIO_RETRIES = 2

    img_completa = None
    for attempt in range(1, MAX_RATIO_RETRIES + 2):
        model, payload = build_payload(slide, position, total, brand_slug=brand_slug, avatar_mode=avatar_mode, formato=formato, refs_fixas=refs_fixas)
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
