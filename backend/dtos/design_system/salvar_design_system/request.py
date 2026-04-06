from pydantic import BaseModel


class DesignSystemRequest(BaseModel):
    nome: str
    slug: str = ""
    cores: dict = {}
    fontes: dict = {}
    pesos: dict = {}
    elementos: dict = {}
    estilo: str = ""
