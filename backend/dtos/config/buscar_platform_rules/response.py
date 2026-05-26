from pydantic import BaseModel
from typing import Optional


class PlataformaRuleResponse(BaseModel):
    nome: str
    max_caracteres: int
    hashtags_max: Optional[int] = None
    specs: Optional[str] = None


class BuscarPlatformRulesResponse(BaseModel):
    plataformas: list[PlataformaRuleResponse]
