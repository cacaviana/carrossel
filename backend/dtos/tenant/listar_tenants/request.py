from pydantic import BaseModel, Field
from typing import Optional


class ListarTenantsRequest(BaseModel):
    limit: int = Field(20, ge=1, le=200)
    offset: int = Field(0, ge=0)
    status: Optional[str] = Field(None, description="Filtro: 'ativo' | 'inativo' | None para todos")
