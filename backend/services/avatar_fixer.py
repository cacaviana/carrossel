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

    # Prompt direto: identifica a pessoa primeiro, depois pede a troca
    num_refs = len(avatares_para_usar)

    # Linguagem NEUTRA de genero. Hardcoding "woman/she/her" quebrava
    # brands com avatar masculino (ex: Carlos da itvalley) — o Gemini recebia
    # pronomes femininos + fotos de homem e ficava confuso, feminizando ou
    # trocando por outra pessoa.
    if num_refs >= 3:
        person_intro = (
            "IMPORTANT: Photos 2, 3, and 4 show the SAME person from different angles. "
            "This is the brand's real content creator. Study their face carefully across "
            "all three photos to understand their identity — face shape, eyes, nose, "
            "mouth, hair, facial hair (if any), skin tone, gender, and approximate age."
        )
    elif num_refs == 2:
        person_intro = (
            "IMPORTANT: Photos 2 and 3 show the SAME person from different angles. "
            "Study their face carefully across both photos to understand their identity, "
            "including gender and approximate age."
        )
    else:
        person_intro = (
            "IMPORTANT: Photo 2 shows the brand's real content creator. "
            "Study their face, gender, and approximate age carefully."
        )

    prompt = (
        f"{person_intro}\n\n"
        f"Photo 1 is a social media post where a DIFFERENT person appears. "
        f"I need you to regenerate photo 1 with the SAME person from photos 2-{num_refs + 1} instead.\n\n"
        f"Requirements:\n"
        f"- The person in the result MUST be the one from photos 2-{num_refs + 1}. Same face, "
        f"same features, same identity, same gender, same age range. Not a different person.\n"
        f"- Do NOT change the gender. If photos 2-{num_refs + 1} show a man, keep him as a man. "
        f"If they show a woman, keep her as a woman. Match exactly.\n"
        f"- Keep the EXACT same scene as photo 1: same pose, same framing, same outfit, "
        f"same lighting, same background, same text, same decorations, same everything.\n"
        f"- The person should look natural in the scene, not pasted. Their face must blend "
        f"with the scene's lighting and skin tone.\n"
        f"- Think of it as: 'if THIS person had posed for photo 1, what would it look like?'\n\n"
        f"No nudity, no violence."
    )
    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "temperature": 0.1,  # baixo pra nao improvisar
            # PASS2 mantem o mesmo aspect ratio da imagem original (4:5 pra carrossel).
            # Default carrossel pq o avatar_fixer nao recebe formato — seguro assumir.
            "imageConfig": {
                "aspectRatio": "4:5",
            },
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
