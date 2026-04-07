from pydantic import BaseModel


class AgenteResponse(BaseModel):
    slug: str
    nome: str
    descricao: str
    tipo: str
    conteudo: str
