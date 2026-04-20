from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class CalendarioItem(BaseModel):
    card_id: str
    title: str
    deadline: datetime
    column_id: str
    priority: str
    pipeline_id: Optional[str] = None
    pdf_url: Optional[str] = None


class ListarCalendarioResponse(BaseModel):
    mes: str
    total: int
    items: list[CalendarioItem]
