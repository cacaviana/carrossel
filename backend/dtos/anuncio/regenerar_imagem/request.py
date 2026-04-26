from typing import Optional
from pydantic import BaseModel, Field


class RegenerarImagemRequest(BaseModel):
    """Dispara regeneracao da imagem inteira (1080x1350)."""
    feedback: Optional[str] = Field(default=None, max_length=500)
    # compat: frontend as vezes manda anuncio_id no body
    anuncio_id: Optional[str] = None
