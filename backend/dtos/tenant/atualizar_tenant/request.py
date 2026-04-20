from pydantic import BaseModel, Field
from typing import Optional

from dtos.tenant.base import LimitesBase


class AtualizarTenantRequest(BaseModel):
    """Atualizacao parcial. Campos ausentes ou None nao sao tocados."""
    nome: Optional[str] = Field(None, min_length=2, max_length=120)
    plano: Optional[str] = None
    limites: Optional[LimitesBase] = None
    status: Optional[str] = None
