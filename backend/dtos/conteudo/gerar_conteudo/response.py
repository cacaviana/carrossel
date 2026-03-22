from pydantic import BaseModel

from dtos.conteudo.base import SlideResponse


class GerarConteudoResponse(BaseModel):
    title: str
    disciplina: str
    tecnologia_principal: str
    hook_formula: str
    slides: list[SlideResponse]
    legenda_linkedin: str
