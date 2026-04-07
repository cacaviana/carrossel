"""Factory de imagem — monta prompts e payloads para Gemini usando PromptComposer (4 camadas)."""

import base64
from pathlib import Path

from factories.prompt_composer import PromptComposer
from services.brand_prompt_builder import get_reference_image_path

def _load_reference_for_brand(brand_slug: str) -> str | None:
    """Carrega imagem de referencia da marca (sem cache — sempre le do disco)."""
    ref_path = get_reference_image_path(brand_slug)
    if ref_path:
        return base64.b64encode(ref_path.read_bytes()).decode()
    return None


def select_model(slide: dict, position: int, total: int) -> str:
    """Pro para capa, codigo e CTA. Flash para content."""
    slide_type = slide.get("type", "content")
    if position == 1 or position == total or slide_type == "code":
        return "gemini-3-pro-image-preview"
    return "gemini-2.5-flash-image"


def build_payload(
    slide: dict,
    position: int,
    total: int,
    foto_criador: str | None = None,
    design_system: str | None = None,
    brand_slug: str | None = None,
    avatar_mode: str = "livre",
    formato: str = "carrossel",
) -> tuple[str, dict]:
    """Retorna (model, payload) prontos para envio a API Gemini."""
    model = select_model(slide, position, total)

    prompt = PromptComposer.compor_prompt_imagem(
        slide, position, total, brand_slug or "", formato=formato
    )

    slide_type = slide.get("type", "content")

    # Assets da marca baseado no avatar_mode
    from services.brand_prompt_builder import get_brand_assets
    usar_assets = False
    if avatar_mode == "sem":
        usar_assets = False
    elif avatar_mode == "capa":
        usar_assets = (position == 1)  # so na capa
    elif avatar_mode == "sim":
        usar_assets = True  # sempre
    elif avatar_mode == "livre":
        usar_assets = True  # art director decide, manda os assets pra ele ter opcao

    assets = get_brand_assets(brand_slug) if (brand_slug and usar_assets) else []

    parts: list[dict] = []
    if assets:
        import random
        refs = random.sample(assets, min(2, len(assets)))
        for ref in refs:
            parts.append({"inline_data": {"mime_type": "image/png", "data": ref}})
        avatar_instruction = (
            "Use the characters/person from the reference images in this slide. "
            "Keep the SAME appearance but in new poses related to the topic. "
        )
        if avatar_mode == "livre":
            avatar_instruction = (
                "You MAY use the characters/person from the reference images if it fits the slide. "
                "If you use them, keep the SAME appearance. You can also choose NOT to include them. "
            )
        parts.append({"text": avatar_instruction + prompt})
    else:
        parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "temperature": 0.9,
        },
    }
    return model, payload
