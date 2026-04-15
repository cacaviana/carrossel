from pydantic import BaseModel
from typing import Optional


class ListarCardsFiltros(BaseModel):
    board_id: Optional[str] = None
    column_id: Optional[str] = None
    priority: Optional[str] = None
    assigned_user_id: Optional[str] = None
    search: Optional[str] = None
