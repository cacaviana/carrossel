from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from dtos.kanban_board.base import ColunaBase


class BoardResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    columns: list[ColunaBase]
    created_at: datetime
    updated_at: Optional[datetime] = None
