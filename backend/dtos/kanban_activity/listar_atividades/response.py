from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AtividadeResponse(BaseModel):
    id: str
    card_id: str
    user_id: str
    user_name: str
    action: str
    metadata: dict = {}
    created_at: datetime
