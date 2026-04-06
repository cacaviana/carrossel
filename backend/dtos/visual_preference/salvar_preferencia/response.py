from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class SalvarPreferenciaResponse(BaseModel):
    id: UUID
    estilo: str
    aprovado: bool
    created_at: datetime
