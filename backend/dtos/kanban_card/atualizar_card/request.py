from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional


class AtualizarCardRequest(BaseModel):
    title: Optional[str] = None
    copy_text: Optional[str] = None
    disciplina: Optional[str] = None
    tecnologia: Optional[str] = None
    priority: Optional[str] = None
    deadline: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def titulo_minimo(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) < 3:
            raise ValueError("Titulo deve ter no minimo 3 caracteres")
        return v.strip() if v else v

    @field_validator("priority")
    @classmethod
    def prioridade_valida(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.lower() not in {"alta", "media", "baixa"}:
            raise ValueError("Prioridade deve ser: alta, media ou baixa")
        return v.lower() if v else v
