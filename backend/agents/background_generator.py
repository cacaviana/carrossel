"""Gera 2-3 backgrounds consistentes via Gemini para usar como base dos slides."""
import os
import asyncio
import logging

import httpx

from mappers.imagem_mapper import extract_image_from_response

from utils.constants import GEMINI_API_URL as API_URL
logger = logging.getLogger(__name__)

# Prompt base pra gerar fundos consistentes (SEM texto)
BG_PROMPT_TEMPLATE = """Generate a dark, premium background image for a LinkedIn carousel slide.

CRITICAL RULES:
- NO TEXT whatsoever. No letters, no words, no numbers, no symbols.
- This is ONLY a background/atmosphere image.
- Dark mode: base color #0A0A0F (almost black, never pure black)
- Subtle purple gradient overlay (#1a0a2e to #0a1628 diagonal)
- Soft purple glow spots (#A78BFA at 6-10% opacity, extreme blur 80px+)
- Optional: subtle green neon accent (#34D399) as small glow in corner
- Style: premium tech, minimal, clean, elegant
- Format: {formato}
- NO robots, NO brains, NO circuits, NO generic tech clipart

Theme/mood for this specific background: {mood}
Variation style: {variacao}
"""

VARIACOES = [
    "Clean gradient with single purple glow spot, extremely minimal",
    "Subtle geometric mesh pattern fading into darkness, abstract tech feel",
    "Dramatic spotlight from top-left, deep shadows, cinematic atmosphere",
]

MOODS = {
    "carrossel": "Vertical 1080x1350, deep dark atmosphere for text overlay",
    "post_unico": "Square 1080x1080, centered composition for single impactful text",
    "thumbnail_youtube": "Horizontal 1280x720, high contrast for YouTube thumbnail",
    "capa_reels": "Tall vertical 1080x1920, full-screen mobile atmosphere for Reels/Stories",
}


async def executar(
    tema: str = "",
    formato: str = "carrossel",
    gemini_api_key: str = "",
    step_id: str = "",
) -> dict:
    """Gera 3 variações de background consistentes."""
    from services.step_progress import atualizar as progress_update, limpar as progress_clear

    if not gemini_api_key:
        gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    mood = MOODS.get(formato, MOODS["carrossel"])
    backgrounds = []
    total = len(VARIACOES)

    async with httpx.AsyncClient(timeout=120.0) as client:
        for i, variacao in enumerate(VARIACOES):
            if step_id:
                progress_update(step_id, i, total, f"Fundo {i + 1}/{total}")

            prompt = BG_PROMPT_TEMPLATE.format(
                formato=formato, mood=mood, variacao=variacao,
            )
            if tema:
                prompt += f"\nSubtle thematic connection to: {tema}"

            modelo = "gemini-2.5-flash-image"  # Flash pra backgrounds (gratis)
            try:
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
                }
                res = await client.post(
                    API_URL.format(model=modelo),
                    json=payload,
                    headers={"x-goog-api-key": gemini_api_key},
                )
                res.raise_for_status()
                image_b64 = extract_image_from_response(res.json())

                backgrounds.append({
                    "variacao": i + 1,
                    "estilo": variacao[:50],
                    "image_base64": image_b64,
                    "modelo": modelo,
                })
            except Exception as e:
                logger.warning("Background %d falhou: %s", i + 1, e)
                backgrounds.append({
                    "variacao": i + 1,
                    "estilo": variacao[:50],
                    "image_base64": None,
                    "erro": str(e),
                })

            await asyncio.sleep(2)

    if step_id:
        progress_clear(step_id)

    return {"backgrounds": backgrounds}
