from pydantic import BaseModel


class RejeitarEtapaResponse(BaseModel):
    sucesso: bool
    etapa_reexecutada: str
    mensagem: str
