from pydantic import BaseModel


class ContadorNaoLidasResponse(BaseModel):
    count: int
