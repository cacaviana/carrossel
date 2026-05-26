from pydantic import BaseModel


class ExcluirAnuncioResponse(BaseModel):
    id: str
    deleted_at: str = ""
    success: bool = True
