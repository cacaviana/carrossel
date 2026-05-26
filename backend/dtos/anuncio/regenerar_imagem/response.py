from pydantic import BaseModel


class RegenerarImagemResponse(BaseModel):
    anuncio_id: str
    pipeline_id: str = ""
    status: str = "gerando"
    message: str = "Regeneracao iniciada"
