from pydantic import BaseModel


class RejeitarEtapaRequest(BaseModel):
    motivo: str = ""
