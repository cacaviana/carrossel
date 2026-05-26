from pydantic import BaseModel
from typing import Optional


class CoresResponse(BaseModel):
    fundo_principal: str
    destaque_primario: str
    destaque_secundario: str
    texto_principal: str
    texto_secundario: str


class BuscarBrandPaletteResponse(BaseModel):
    cores: CoresResponse
    fonte: str
    elementos_obrigatorios: list[str]
    estilo: str
