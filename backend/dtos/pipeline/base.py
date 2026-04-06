from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class EtapaBase(BaseModel):
    agente: str
    ordem: int
    status: str
    erro_mensagem: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class PipelineBase(BaseModel):
    tema: str
    formato: str
    modo_funil: bool = False
    status: str
    etapa_atual: Optional[str] = None
