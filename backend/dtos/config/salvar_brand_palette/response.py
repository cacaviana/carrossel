from pydantic import BaseModel


class SalvarBrandPaletteResponse(BaseModel):
    sucesso: bool
    mensagem: str
