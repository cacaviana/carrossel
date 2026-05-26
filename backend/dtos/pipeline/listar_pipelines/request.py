from pydantic import BaseModel
from typing import Optional


class ListarPipelinesFiltros(BaseModel):
    formato: Optional[str] = None
    status: Optional[str] = None
    limit: int = 50
    offset: int = 0
