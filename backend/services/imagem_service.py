import asyncio

import httpx

from factories.imagem_factory import build_payload
from mappers.imagem_mapper import extract_image_from_response
from services.foto_overlay import overlay_foto

from utils.constants import GEMINI_API_URL as API_URL


async def gerar_imagem_slide(
    slide: dict,
    slide_index: int,
    total_slides: int,
    gemini_api_key: str,
    foto_criador: str | None = None,
    design_system: str | None = None,
    brand_slug: str | None = None,
    formato: str = "carrossel",
) -> str | None:
    position = slide_index + 1
    model, payload = build_payload(slide, position, total_slides, foto_criador, design_system, brand_slug=brand_slug, formato=formato)

    async with httpx.AsyncClient(timeout=120.0) as client:
        res = await client.post(
            API_URL.format(model=model),
            json=payload,
            headers={"x-goog-api-key": gemini_api_key},
        )
        res.raise_for_status()
        raw_image = extract_image_from_response(res.json())
        if raw_image and foto_criador:
            is_cta = slide.get("type") == "cta"
            raw_image = overlay_foto(raw_image, foto_criador, is_cta=is_cta, posicao=position, total=total_slides)
        return raw_image


async def gerar_imagens(
    slides: list[dict],
    gemini_api_key: str,
    foto_criador: str | None = None,
    design_system: str | None = None,
    brand_slug: str | None = None,
) -> list[str | None]:
    images: list[str | None] = []
    total = len(slides)

    async with httpx.AsyncClient(timeout=120.0) as client:
        for i, slide in enumerate(slides):
            position = i + 1
            model, payload = build_payload(slide, position, total, foto_criador, design_system, brand_slug=brand_slug)

            try:
                res = await client.post(
                    API_URL.format(model=model),
                    json=payload,
                    headers={"x-goog-api-key": gemini_api_key},
                )
                res.raise_for_status()
                raw_image = extract_image_from_response(res.json())
                if raw_image and foto_criador:
                    is_cta = slide.get("type") == "cta"
                    raw_image = overlay_foto(raw_image, foto_criador, is_cta=is_cta, posicao=position, total=total)
                images.append(raw_image)
            except Exception as e:
                print(f"Erro no slide {i + 1}: {e}")
                images.append(None)

            if i < total - 1:
                await asyncio.sleep(2)

    # Pos-producao: validar texto com visao e regenerar erros
    from services.text_validator import validar_e_regenerar

    async def _regenerar_slide(slide, idx, total_s):
        return await gerar_imagem_slide(
            slide, idx, total_s, gemini_api_key,
            foto_criador=foto_criador, design_system=design_system, brand_slug=brand_slug,
        )

    images = await validar_e_regenerar(
        slides, images, _regenerar_slide, gemini_api_key,
    )

    return images
