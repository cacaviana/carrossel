from pydantic import BaseModel
from typing import Optional

from dtos.tenant.base import LimitesBase, BrandingDefaultBase


class CriarTenantResponse(BaseModel):
    tenant_id: str
    nome: str
    plano: str
    status: str
    limites: LimitesBase
    branding_default: BrandingDefaultBase
    admin_user_id: str
    admin_email: str
    created_at: str
    created_by: Optional[str] = None
