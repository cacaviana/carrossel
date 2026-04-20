from pydantic import BaseModel
from typing import Optional


class ValidarApiKeyResponse(BaseModel):
    ok: bool
    provider: str
    erro: Optional[str] = None
    detalhe: Optional[str] = None
