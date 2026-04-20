from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from dtos.tenant.base import TenantBase, BrandingDefaultBase, LimitesBase


class AdminInicialRequest(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(..., min_length=6)


class CriarTenantRequest(BaseModel):
    tenant_id: str = Field(..., min_length=3, max_length=40, pattern=r"^[a-z0-9][a-z0-9-]*[a-z0-9]$",
                           description="Slug unico em lowercase. Usado em JWTs e namespaces de arquivos.")
    nome: str = Field(..., min_length=2, max_length=120)
    plano: str = Field(..., description="free | pro | enterprise")
    limites: LimitesBase
    branding_default: Optional[BrandingDefaultBase] = None
    admin: AdminInicialRequest
