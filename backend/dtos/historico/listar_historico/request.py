from pydantic import BaseModel
from typing import Optional
from datetime import date


class ListarHistoricoFiltros(BaseModel):
    texto: Optional[str] = None
    formato: Optional[str] = None
    status: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    limit: int = 50
    offset: int = 0
