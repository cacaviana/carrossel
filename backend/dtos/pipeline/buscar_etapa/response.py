from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Any


class BuscarEtapaResponse(BaseModel):
    id: UUID
    agente: str
    ordem: int
    status: str
    entrada: Optional[Any] = None
    saida: Optional[Any] = None
    erro_mensagem: Optional[str] = None
    aprovado_por: Optional[str] = None
    approved_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
