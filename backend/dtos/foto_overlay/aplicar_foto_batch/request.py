from pydantic import BaseModel


class AplicarFotoBatchRequest(BaseModel):
    slides: list[str]
    foto_criador: str
