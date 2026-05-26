from pydantic import BaseModel
from typing import Optional

from dtos.tenant.base import LimitesBase


class TenantListItem(BaseModel):
    tenant_id: str
    nome: str
    plano: str
    status: str
    limites: LimitesBase
    created_at: Optional[str] = None


class ListarTenantsResponse(BaseModel):
    items: list[TenantListItem]
    total: int
    limit: int
    offset: int
