from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ComentarioResponse(BaseModel):
    id: str
    card_id: str
    user_id: str
    user_name: str
    user_avatar_url: Optional[str] = None
    text: str
    created_at: datetime
    updated_at: Optional[datetime] = None
