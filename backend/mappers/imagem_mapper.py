"""Mapper de imagem — extrai base64 da response Gemini."""


def extract_image_from_response(data: dict) -> str | None:
    """Extrai data URI base64 da resposta da Gemini API."""
    candidates = data.get("candidates", [])
    if not candidates:
        return None
    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        if "inlineData" in part:
            b64 = part["inlineData"]["data"]
            mime = part["inlineData"].get("mimeType", "image/png")
            return f"data:{mime};base64,{b64}"
    return None
