from pydantic import BaseModel


class SalvarCreatorRegistryResponse(BaseModel):
    sucesso: bool
    total_criadores: int
    mensagem: str
