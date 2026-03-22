import asyncio

import httpx

from factories.imagem_factory import build_payload
from mappers.imagem_mapper import extract_image_from_response

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


async def gerar_imagem_slide(
    slide: dict,
    slide_index: int,
    total_slides: int,
    gemini_api_key: str,
    foto_criador: str | None = None,
) -> str | None:
    position = slide_index + 1
    model, payload = build_payload(slide, position, total_slides, foto_criador)

    async with httpx.AsyncClient(timeout=120.0) as client:
        res = await client.post(
            API_URL.format(model=model),
            json=payload,
            headers={"x-goog-api-key": gemini_api_key},
        )
        res.raise_for_status()
        return extract_image_from_response(res.json())


async def gerar_imagens(
    slides: list[dict],
    gemini_api_key: str,
    foto_criador: str | None = None,
) -> list[str | None]:
    images: list[str | None] = []
    total = len(slides)

    async with httpx.AsyncClient(timeout=120.0) as client:
        for i, slide in enumerate(slides):
            position = i + 1
            model, payload = build_payload(slide, position, total, foto_criador)

            try:
                res = await client.post(
                    API_URL.format(model=model),
                    json=payload,
                    headers={"x-goog-api-key": gemini_api_key},
                )
                res.raise_for_status()
                images.append(extract_image_from_response(res.json()))
            except Exception as e:
                print(f"Erro no slide {i + 1}: {e}")
                images.append(None)

            if i < total - 1:
                await asyncio.sleep(2)

    return images
