from pydantic import BaseModel


class AplicarFotoResponse(BaseModel):
    image: str
