"""Ajusta imagem existente com feedback do usuario.

Envia a imagem anterior + referencia de estilo + feedback e pede ao Gemini:
"mantem tudo, so aplica esse ajuste".
"""
import httpx

from mappers.imagem_mapper import extract_image_from_response
from utils.constants import GEMINI_API_URL as API_URL


async def ajustar_imagem(
    client: httpx.AsyncClient,
    image_b64: str,
    feedback: str,
    api_key: str,
    ref_image_b64: str | None = None,
    modelo: str = "gemini-2.0-flash-exp",
) -> dict:
    """Aplica ajuste minimo na imagem baseado no feedback.

    Retorna: {"image": base64, "ajustado": True/False}
    """
    img = image_b64.split(",")[1] if "," in image_b64 else image_b64

    parts = []

    # Imagem anterior (a que precisa ajustar)
    parts.append({"inline_data": {"mime_type": "image/png", "data": img}})

    # Referência de estilo (se existir)
    if ref_image_b64:
        ref = ref_image_b64.split(",")[1] if "," in ref_image_b64 else ref_image_b64
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": ref}})

    parts.append({"text": (
        f"The first image is a post I already created. "
        f"{'The second image is the style reference. ' if ref_image_b64 else ''}"
        f"I need you to make ONE small adjustment to the first image:\n\n"
        f"{feedback}\n\n"
        f"IMPORTANT: Keep EVERYTHING else exactly the same — same person, same text, "
        f"same colors, same doodles, same composition, same style. "
        f"ONLY change what I asked. Minimal edit."
    )})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "temperature": 0.3,
        },
    }

    try:
        res = await client.post(
            API_URL.format(model=modelo),
            json=payload,
            headers={"x-goog-api-key": api_key},
        )
        res.raise_for_status()
        new_img = extract_image_from_response(res.json())
        if new_img:
            return {"image": new_img, "ajustado": True}
    except Exception as e:
        print(f"Erro ao ajustar imagem: {e}")

    return {"image": image_b64, "ajustado": False}
