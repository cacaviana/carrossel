from pydantic import BaseModel


class CoresResponse(BaseModel):
    fundo_principal: str
    destaque_primario: str
    destaque_secundario: str
    texto_principal: str
    texto_secundario: str


class BrandPaletteResponse(BaseModel):
    cores: CoresResponse
    fonte: str
    estilo: str
    elementos_obrigatorios: list[str]


class RulesResponse(BaseModel):
    max_caracteres: int
    hashtags_max: int | None = None
    specs: str | None = None


class PlataformaResponse(BaseModel):
    id: str
    nome: str
    ativo: bool
    rules: RulesResponse
    brand_palette: BrandPaletteResponse


class BuscarPlataformasResponse(BaseModel):
    plataformas: list[PlataformaResponse]


class SalvarPlataformasResponse(BaseModel):
    sucesso: bool
    mensagem: str
