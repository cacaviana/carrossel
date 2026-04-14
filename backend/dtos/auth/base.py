"""Campos compartilhados do dominio Auth."""

from pydantic import BaseModel, EmailStr


class UsuarioBase(BaseModel):
    """Campos comuns a todo usuario."""
    email: EmailStr
    name: str
    role: str  # admin | copywriter | designer | reviewer | viewer
