from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class PreferenciaItem(BaseModel):
    id: UUID
    estilo: str
    aprovado: bool
    contexto: Optional[dict] = None
    created_at: datetime


class ListarPreferenciasResponse(BaseModel):
    items: list[PreferenciaItem]
