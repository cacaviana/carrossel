"""Factory de imagem — monta prompts e payloads para Gemini."""

from services.prompt_templates import build_prompt


def select_model(slide: dict, position: int, total: int) -> str:
    """Pro para capa, todo slide de código e CTA. Flash para o resto."""
    slide_type = slide.get("type", "content")
    if position == 1 or position == total or slide_type == "code":
        return "gemini-3-pro-image-preview"
    return "gemini-2.5-flash-image"


def build_image_prompt(slide: dict, position: int, total: int, design_system: str | None = None) -> str:
    """Delega para prompt_templates.build_prompt."""
    return build_prompt(slide, position, total, design_system)


def build_payload(
    slide: dict,
    position: int,
    total: int,
    foto_criador: str | None = None,
    design_system: str | None = None,
) -> tuple[str, dict]:
    """Retorna (model, payload) prontos para envio à API Gemini."""
    model = select_model(slide, position, total)
    prompt = build_image_prompt(slide, position, total, design_system)
    parts: list[dict] = []

    # Foto do criador no último slide (CTA)
    if position == total and foto_criador:
        foto_data = foto_criador.split(",", 1)[1] if "," in foto_criador else foto_criador
        parts.append({"inlineData": {"mimeType": "image/jpeg", "data": foto_data}})

    parts.append({"text": prompt})
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
    }
    return model, payload
