from pydantic import BaseModel
from typing import Optional


class CriadorRequest(BaseModel):
    nome: str
    funcao: str
    plataforma: str
    url: Optional[str] = None
    ativo: bool = True


class SalvarCreatorRegistryRequest(BaseModel):
    criadores: list[CriadorRequest]
