from pydantic import BaseModel


class GerarImagemResponse(BaseModel):
    images: list[str | None]


class GerarImagemSlideResponse(BaseModel):
    image: str | None
