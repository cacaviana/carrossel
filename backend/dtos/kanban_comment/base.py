from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ComentarioBase(BaseModel):
    text: str
    user_id: str
    user_name: str
    user_avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
