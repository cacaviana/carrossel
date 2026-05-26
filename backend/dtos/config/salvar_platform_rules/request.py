from pydantic import BaseModel
from typing import Optional


class PlataformaRuleRequest(BaseModel):
    nome: str
    max_caracteres: int
    hashtags_max: Optional[int] = None
    specs: Optional[str] = None


class SalvarPlatformRulesRequest(BaseModel):
    plataformas: list[PlataformaRuleRequest]
