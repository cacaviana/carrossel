from pydantic import BaseModel


class CoresRequest(BaseModel):
    fundo_principal: str
    destaque_primario: str
    destaque_secundario: str
    texto_principal: str
    texto_secundario: str


class BrandPaletteRequest(BaseModel):
    cores: CoresRequest
    fonte: str
    estilo: str
    elementos_obrigatorios: list[str]


class RulesRequest(BaseModel):
    max_caracteres: int
    hashtags_max: int | None = None
    specs: str | None = None


class PlataformaRequest(BaseModel):
    id: str
    nome: str
    ativo: bool
    rules: RulesRequest
    brand_palette: BrandPaletteRequest


class SalvarPlataformasRequest(BaseModel):
    plataformas: list[PlataformaRequest]
