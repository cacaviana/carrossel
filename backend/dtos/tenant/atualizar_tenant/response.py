from pydantic import BaseModel
from typing import Optional

from dtos.tenant.base import LimitesBase, BrandingDefaultBase


class AtualizarTenantResponse(BaseModel):
    tenant_id: str
    nome: str
    plano: str
    status: str
    limites: LimitesBase
    branding_default: Optional[BrandingDefaultBase] = None
    updated_at: str
    updated_by: Optional[str] = None
