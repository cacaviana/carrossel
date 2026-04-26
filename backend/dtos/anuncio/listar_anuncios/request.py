from typing import Optional
from pydantic import BaseModel, Field


class ListarAnunciosRequest(BaseModel):
    """Query params da listagem (mapeados no router)."""
    busca: Optional[str] = None
    status: Optional[str] = None
    etapa_funil: Optional[str] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    incluir_excluidos: bool = False
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=100, ge=1, le=500)
