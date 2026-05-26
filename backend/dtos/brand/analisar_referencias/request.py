from pydantic import BaseModel


class AnalisarReferenciasRequest(BaseModel):
    imagens: list[str]  # lista de base64 (2-5 imagens)
    nome_marca: str = ""  # nome da marca (opcional, ajuda no contexto)
    descricao: str = ""  # descricao curta do negocio (opcional)
