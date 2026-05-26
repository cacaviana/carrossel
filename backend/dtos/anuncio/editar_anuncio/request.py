from typing import Optional
from pydantic import BaseModel, Field


class EditarAnuncioRequest(BaseModel):
    """Edicao de copy + metadados. NAO regenera imagem (ha endpoint proprio)."""
    titulo: Optional[str] = Field(default=None, min_length=3, max_length=200)
    headline: Optional[str] = Field(default=None, min_length=1, max_length=40)
    descricao: Optional[str] = Field(default=None, min_length=1, max_length=125)
    cta: Optional[str] = Field(default=None, min_length=1, max_length=30)
    etapa_funil: Optional[str] = None
    # compat: frontend as vezes manda o id no body junto do path
    id: Optional[str] = None
