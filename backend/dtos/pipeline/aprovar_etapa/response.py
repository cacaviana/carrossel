from pydantic import BaseModel


class AprovarEtapaResponse(BaseModel):
    sucesso: bool
    proxima_etapa: str | None = None
    mensagem: str
