from pydantic import BaseModel


class GerarConteudoRequest(BaseModel):
    disciplina: str | None = None
    tecnologia: str | None = None
    tema_custom: str | None = None
    texto_livre: str | None = None
    total_slides: int = 10
