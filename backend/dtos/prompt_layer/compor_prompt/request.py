from pydantic import BaseModel
from typing import Optional


class ComporPromptRequest(BaseModel):
    tipo: str  # "texto" ou "imagem"
    brand_slug: str
    formato: str  # "carrossel", "post_unico", "thumbnail_youtube", "capa_reels"
    slide: dict  # dados do slide (type, headline, bullets, code, etc)
    position: int = 1
    total: int = 7
    avatar_mode: str = "livre"
    agente: Optional[str] = None  # "strategist", "copywriter", etc (para tipo=texto)
