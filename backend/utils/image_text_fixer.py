"""Corrige texto em imagem preservando o visual original.

Envia a imagem como referencia e pede ao Gemini: "mantem tudo, so corrige o texto".
Valida com OCR apos cada tentativa. Usado tanto na geracao automatica quanto no editor.
"""
import asyncio

import httpx

from mappers.imagem_mapper import extract_image_from_response
from utils.constants import GEMINI_API_URL as API_URL

PROMPTS_VARIACAO = [
    "Keep the EXACT same style, colors, characters, layout.",
    "Maintain identical visual design. Same atmosphere, same elements.",
    "Copy the visual style precisely. Same background, same cards.",
]

TEMPS = [0.2, 0.3, 0.4]


async def corrigir_texto_na_imagem(
    client: httpx.AsyncClient,
    image_b64: str,
    titulo: str,
    corpo: str,
    api_key: str,
    max_tentativas: int = 3,
    modelo: str = "gemini-3-pro-image-preview",
) -> dict:
    """Tenta corrigir o texto na imagem ate max_tentativas vezes.

    Retorna:
        {"image": base64, "corrigido": True/False, "tentativas": int, "texto_lido": str}
    """
    img_atual = image_b64.split(",")[1] if "," in image_b64 else image_b64
    melhor_img = None
    texto_lido = ""

    for tentativa in range(max_tentativas):
        var = PROMPTS_VARIACAO[tentativa % len(PROMPTS_VARIACAO)]
        prompt = (
            f"This image is visually PERFECT. {var} "
            f"The ONLY thing to change is the text. Replace ALL text with EXACTLY: "
            f"Title: \"{titulo}\" "
        )
        if corpo:
            prompt += f"Body: \"{corpo}\" "
        if tentativa > 0 and texto_lido:
            prompt += f"PREVIOUS ATTEMPT HAD WRONG TEXT: \"{texto_lido[:80]}\". FIX IT. "
        prompt += "COPY every letter EXACTLY. Do NOT add extra text."

        try:
            res = await client.post(
                API_URL.format(model=modelo),
                json={
                    "contents": [{"parts": [
                        {"inline_data": {"mime_type": "image/png", "data": img_atual}},
                        {"text": prompt},
                    ]}],
                    "generationConfig": {
                        "responseModalities": ["IMAGE", "TEXT"],
                        "temperature": TEMPS[tentativa % len(TEMPS)],
                    },
                },
                headers={"x-goog-api-key": api_key},
            )
            res.raise_for_status()
            new_img = extract_image_from_response(res.json())
        except Exception:
            new_img = None

        if not new_img:
            continue
        melhor_img = new_img

        # OCR pra verificar
        raw_new = new_img.split(",")[1] if "," in new_img else new_img
        texto_lido = await _ocr_imagem(client, raw_new, api_key)

        if titulo.lower().strip() in texto_lido.lower():
            return {
                "image": melhor_img,
                "corrigido": True,
                "tentativas": tentativa + 1,
                "texto_lido": texto_lido[:200],
            }

        # Proxima tentativa usa a imagem corrigida como base
        img_atual = raw_new
        if tentativa < max_tentativas - 1:
            await asyncio.sleep(2)

    return {
        "image": melhor_img or image_b64,
        "corrigido": False,
        "tentativas": max_tentativas,
        "texto_lido": texto_lido[:200],
    }


async def _ocr_imagem(client: httpx.AsyncClient, image_b64: str, api_key: str) -> str:
    """Le texto da imagem via Gemini Flash (OCR)."""
    try:
        res = await client.post(
            API_URL.format(model="gemini-2.5-flash"),
            json={"contents": [{"parts": [
                {"inline_data": {"mime_type": "image/png", "data": image_b64}},
                {"text": "Read ALL text in this image. Return ONLY the text."},
            ]}]},
            headers={"x-goog-api-key": api_key},
        )
        texto = ""
        for cand in res.json().get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                if "text" in part:
                    texto += part["text"]
        return texto
    except Exception:
        return ""
