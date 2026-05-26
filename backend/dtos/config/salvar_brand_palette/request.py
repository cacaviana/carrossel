from pydantic import BaseModel


class CoresRequest(BaseModel):
    fundo_principal: str
    destaque_primario: str
    destaque_secundario: str
    texto_principal: str
    texto_secundario: str


class SalvarBrandPaletteRequest(BaseModel):
    cores: CoresRequest
    fonte: str
    elementos_obrigatorios: list[str]
    estilo: str
