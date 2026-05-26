from pydantic import BaseModel


class PublicacaoResult(BaseModel):
    platform: str
    conta: str
    post_id: str | None = None
    error: str | None = None


class PublicarResponse(BaseModel):
    resultados: list[PublicacaoResult]
