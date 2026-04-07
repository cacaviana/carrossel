from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HistoricoItemBase(BaseModel):
    titulo: str
    formato: Optional[str] = None
    status: Optional[str] = None
    disciplina: Optional[str] = None
    tecnologia_principal: Optional[str] = None
    total_slides: Optional[int] = None
    final_score: Optional[float] = None
    google_drive_link: Optional[str] = None
    created_at: Optional[datetime] = None
