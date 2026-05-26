from pydantic import BaseModel, Field
from typing import Literal


class ValidarApiKeyRequest(BaseModel):
    """Valida uma chave de API ANTES de salvar. Ping trivial ao provider."""
    provider: Literal["claude", "gemini", "openai", "drive"]
    api_key: str = Field(..., min_length=1, description="Chave a validar. Para drive, JSON da service account.")
