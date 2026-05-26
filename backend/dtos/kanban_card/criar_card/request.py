from pydantic import BaseModel, field_validator
from typing import Optional


class CriarCardRequest(BaseModel):
    title: str
    copy_text: Optional[str] = None
    disciplina: Optional[str] = None
    tecnologia: Optional[str] = None
    priority: str = "media"
    assigned_user_ids: list[str] = []
    pipeline_id: Optional[str] = None

    @field_validator("title")
    @classmethod
    def titulo_minimo(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError("Titulo deve ter no minimo 3 caracteres")
        return v.strip()

    @field_validator("priority")
    @classmethod
    def prioridade_valida(cls, v: str) -> str:
        if v.lower() not in {"alta", "media", "baixa"}:
            raise ValueError("Prioridade deve ser: alta, media ou baixa")
        return v.lower()
