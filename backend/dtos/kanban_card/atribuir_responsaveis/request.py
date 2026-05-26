from pydantic import BaseModel


class AtribuirResponsaveisRequest(BaseModel):
    user_ids: list[str]
