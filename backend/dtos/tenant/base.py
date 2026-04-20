from pydantic import BaseModel, Field
from typing import Optional


PLANOS_VALIDOS = ("free", "pro", "enterprise")
STATUS_VALIDOS = ("ativo", "inativo")


class LimitesBase(BaseModel):
    creditos_mes: int = Field(..., ge=0, description="Creditos de geracao por mes")
    marcas_max: int = Field(..., ge=1, description="Numero maximo de marcas permitidas")


class BrandingDefaultBase(BaseModel):
    """Paleta neutra + fonte default aplicada a novos tenants."""
    paleta_fundo: str = "#0A0A0A"
    paleta_texto: str = "#FAFAFA"
    paleta_destaque: str = "#A78BFA"
    fonte: str = "Outfit"


class TenantBase(BaseModel):
    """Campos compartilhados entre criar/atualizar/response."""
    nome: str = Field(..., min_length=2, max_length=120)
    plano: str = Field(..., description=f"Um de: {', '.join(PLANOS_VALIDOS)}")
    limites: LimitesBase
    branding_default: Optional[BrandingDefaultBase] = None
