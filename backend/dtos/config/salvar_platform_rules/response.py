from pydantic import BaseModel


class SalvarPlatformRulesResponse(BaseModel):
    sucesso: bool
    mensagem: str
