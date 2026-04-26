from typing import Optional
from pydantic import BaseModel, field_validator


class ExportarAnuncioRequest(BaseModel):
    """Destino: 'png' (retorna imagem base64) | 'drive' (salva no Drive)."""
    destino: str = "png"
    drive_parent_folder_id: Optional[str] = None

    @field_validator("destino")
    @classmethod
    def destino_valido(cls, v: str) -> str:
        if v not in {"png", "drive"}:
            raise ValueError("destino deve ser 'png' ou 'drive'")
        return v
