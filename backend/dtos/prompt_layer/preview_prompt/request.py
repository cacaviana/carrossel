from pydantic import BaseModel
from typing import Optional


class PreviewPromptRequest(BaseModel):
    tipo: str  # "texto" ou "imagem"
    brand_slug: str
    formato: str
    slide_type: str = "content"
    position: int = 1
    total: int = 7
