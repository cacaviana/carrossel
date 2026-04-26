from pydantic import BaseModel


class CriarAnuncioResponse(BaseModel):
    """Resposta enxuta ao criar -- frontend usa apenas anuncio_id + pipeline_id."""
    anuncio_id: str
    pipeline_id: str
    status: str
