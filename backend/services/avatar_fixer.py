"""Corrige avatar em imagem gerada — usa o mesmo ajustar_imagem que ja funciona.

Pega o avatar da marca como referencia e pede pro Gemini trocar a pessoa.
"""

import os

import httpx

from factories.imagem_factory import _load_avatars
from utils.image_adjuster import ajustar_imagem


async def corrigir_avatar(
    imagem_b64: str,
    brand_slug: str,
    gemini_api_key: str = "",
) -> str:
    """Troca a pessoa na imagem pelo avatar da marca.

    Usa o mesmo image_adjuster que ja funcionou antes —
    manda a imagem + avatar como ref + feedback de trocar a pessoa.
    """
    avatars = _load_avatars(brand_slug)
    if not avatars:
        raise ValueError(f"Nenhum avatar encontrado para marca '{brand_slug}'")

    # Maior avatar = melhor qualidade
    avatar_b64 = max(avatars, key=len)

    if not gemini_api_key:
        gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    feedback = (
        "Replace the person in this image with the person from the reference photo. "
        "Keep the same pose, same position, same framing. "
        "Change ONLY the person's face and appearance. Everything else stays identical."
    )

    async with httpx.AsyncClient(timeout=120) as client:
        result = await ajustar_imagem(
            client=client,
            image_b64=imagem_b64,
            feedback=feedback,
            api_key=gemini_api_key,
            ref_image_b64=avatar_b64,
        )

    if result.get("ajustado") and result.get("image"):
        return result["image"]

    raise RuntimeError("Gemini nao conseguiu ajustar o avatar")
