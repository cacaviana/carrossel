from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

from dtos.pipeline.base import EtapaBase


class BuscarEtapaDetalhe(EtapaBase):
    id: UUID
    entrada_resumo: Optional[str] = None
    saida_resumo: Optional[str] = None
    aprovado_por: Optional[str] = None
    approved_at: Optional[datetime] = None


class BuscarPipelineResponse(BaseModel):
    id: UUID
    tema: str
    formato: str
    modo_funil: bool
    status: str
    etapa_atual: Optional[str]
    modo_entrada: Optional[str]
    disciplina: Optional[str]
    tecnologia: Optional[str]
    etapas: list[BuscarEtapaDetalhe]
    created_at: datetime
    updated_at: Optional[datetime]
