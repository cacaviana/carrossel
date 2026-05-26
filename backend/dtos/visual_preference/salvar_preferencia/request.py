from pydantic import BaseModel
from typing import Optional


class SalvarPreferenciaRequest(BaseModel):
    estilo: str
    aprovado: bool
    contexto: Optional[dict] = None
