from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime


class BuscarHistoricoResponse(BaseModel):
    id: UUID
    titulo: str
    formato: Optional[str] = None
    status: Optional[str] = None
    disciplina: Optional[str] = None
    tecnologia_principal: Optional[str] = None
    tipo_carrossel: Optional[str] = None
    total_slides: Optional[int] = None
    final_score: Optional[float] = None
    legenda_linkedin: Optional[str] = None
    google_drive_link: Optional[str] = None
    google_drive_folder_name: Optional[str] = None
    pipeline_id: Optional[str] = None
    created_at: Optional[datetime] = None
