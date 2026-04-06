from pydantic import BaseModel


class AplicarFotoBatchResponse(BaseModel):
    images: list[str]
