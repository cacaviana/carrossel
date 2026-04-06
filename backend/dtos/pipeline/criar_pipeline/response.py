from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

from dtos.pipeline.base import EtapaBase


class CriarPipelineResponse(BaseModel):
    id: UUID
    tema: str
    formato: str
    modo_funil: bool
    status: str
    etapa_atual: Optional[str]
    etapas: list[EtapaBase]
    created_at: datetime
