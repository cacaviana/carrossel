from pydantic import BaseModel


class AplicarFotoRequest(BaseModel):
    slide_image: str
    foto_criador: str
    is_cta: bool = False
