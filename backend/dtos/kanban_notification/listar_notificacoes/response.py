from pydantic import BaseModel
from datetime import datetime


class NotificacaoResponse(BaseModel):
    id: str
    card_id: str
    type: str
    message: str
    is_read: bool
    created_at: datetime
