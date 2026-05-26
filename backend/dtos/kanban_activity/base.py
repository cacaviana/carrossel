from pydantic import BaseModel
from datetime import datetime


class AtividadeBase(BaseModel):
    action: str
    user_id: str
    user_name: str
    metadata: dict = {}
    created_at: datetime
