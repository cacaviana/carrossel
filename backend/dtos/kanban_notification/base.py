from pydantic import BaseModel
from datetime import datetime


class NotificacaoBase(BaseModel):
    type: str
    message: str
    card_id: str
    is_read: bool
    created_at: datetime
