from pydantic import BaseModel
from typing import Optional


class CriadorResponse(BaseModel):
    nome: str
    funcao: str
    plataforma: str
    url: Optional[str] = None
    ativo: bool


class BuscarCreatorRegistryResponse(BaseModel):
    criadores: list[CriadorResponse]
