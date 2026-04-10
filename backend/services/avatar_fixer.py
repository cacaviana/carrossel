"""Corrige avatar em imagem gerada — face swap com multiplas fotos do avatar.

Manda a imagem original + 3 fotos do avatar pro Gemini entender a pessoa
de angulos diferentes, e pede pra EDITAR (nao regerar) so trocando o rosto.
"""

import os

import httpx

from factories.imagem_factory import _load_avatars
from mappers.imagem_mapper import extract_image_from_response
from utils.constants import GEMINI_API_URL


async def corrigir_avatar(
    imagem_b64: str,
    brand_slug: str,
    gemini_api_key: str = "",
) -> str:
    """Troca a pessoa na imagem pelo avatar da marca.

    Manda 3 fotos do avatar como referencia multi-angulo pra Gemini
    entender a identidade e editar apenas o rosto da pessoa na imagem.
    """
    avatars = _load_avatars(brand_slug)
    if not avatars:
        raise ValueError(f"Nenhum avatar encontrado para marca '{brand_slug}'")

    if not gemini_api_key:
        gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    # Usar ate 3 avatares de angulos diferentes (quanto mais melhor pro Gemini)
    avatares_para_usar = avatars[:3]
    print(f"[avatar_fixer] Usando {len(avatares_para_usar)} fotos do avatar")

    img_raw = imagem_b64.split(",")[1] if "," in imagem_b64 else imagem_b64

    # Montar parts: primeira e a imagem a editar, depois as refs do avatar
    parts = [
        {"inline_data": {"mime_type": "image/png", "data": img_raw}},
    ]
    for i, av in enumerate(avatares_para_usar, start=2):
        av_raw = av.split(",")[1] if "," in av else av
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": av_raw}})

    # Prompt super especifico: EDIT nao REGENERATE
    num_refs = len(avatares_para_usar)
    ref_label = f"photos 2 to {num_refs + 1}" if num_refs > 1 else "photo 2"

    prompt = (
        f"TASK: Edit the FIRST image. Do NOT regenerate it.\n\n"
        f"The first image is a social media post I already created. "
        f"I want to keep this EXACT image — same text, same fonts, same colors, "
        f"same layout, same background, same decorations, same EVERYTHING.\n\n"
        f"The {ref_label} show the person I want in the image (multiple angles of the same person).\n\n"
        f"EDIT ONLY the face and hair of the person in the first image to match the person "
        f"in the reference photos. Keep the SAME pose, same body position, same clothing, "
        f"same framing. Only swap the face.\n\n"
        f"Think of it as face-swapping in the same photo, not creating a new image. "
        f"Every single pixel outside the face area must remain IDENTICAL to the first image.\n\n"
        f"No nudity, no violence."
    )
    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "temperature": 0.1,  # baixo pra nao improvisar
        },
    }

    model = "gemini-3-pro-image-preview"
    url = GEMINI_API_URL.format(model=model)

    async with httpx.AsyncClient(timeout=120) as client:
        try:
            resp = await client.post(
                url,
                json=payload,
                headers={"x-goog-api-key": gemini_api_key},
            )
            if resp.status_code != 200:
                print(f"[avatar_fixer] Pro falhou ({resp.status_code}): {resp.text[:200]}")
                # Fallback pra Flash
                model2 = "gemini-2.5-flash-image"
                url2 = GEMINI_API_URL.format(model=model2)
                resp = await client.post(
                    url2,
                    json=payload,
                    headers={"x-goog-api-key": gemini_api_key},
                )
            resp.raise_for_status()
            new_img = extract_image_from_response(resp.json())
            if new_img:
                return new_img
        except Exception as e:
            print(f"[avatar_fixer] Erro: {e}")

    raise RuntimeError("Gemini nao conseguiu trocar o avatar")
