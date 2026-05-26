from pydantic import BaseModel
from typing import Optional


class VisualPreferenceBase(BaseModel):
    estilo: str
    aprovado: bool
    contexto: Optional[dict] = None
