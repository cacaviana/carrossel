from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class PipelineResumo(BaseModel):
    id: UUID
    tema: str
    formato: str
    status: str
    etapa_atual: Optional[str]
    final_score: Optional[float] = None
    created_at: datetime


class ListarPipelinesResponse(BaseModel):
    items: list[PipelineResumo]
    total: int
