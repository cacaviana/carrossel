"""Request de criacao de usuario (admin cria diretamente)."""

import re

from pydantic import BaseModel, EmailStr, field_validator


class CriarUsuarioRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str = "viewer"  # admin | copywriter | designer | reviewer | viewer
    avatar_url: str | None = None

    @field_validator("password")
    @classmethod
    def senha_forte(cls, v: str) -> str:
        """RN-021: min 8 chars, 1 maiuscula, 1 numero, 1 caractere especial."""
        if len(v) < 8:
            raise ValueError("Senha deve ter no minimo 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Senha deve conter pelo menos 1 letra maiuscula")
        if not re.search(r"[0-9]", v):
            raise ValueError("Senha deve conter pelo menos 1 numero")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Senha deve conter pelo menos 1 caractere especial")
        return v

    @field_validator("role")
    @classmethod
    def role_valido(cls, v: str) -> str:
        roles_validos = {"admin", "copywriter", "designer", "reviewer", "viewer"}
        if v not in roles_validos:
            raise ValueError(f"Role invalido. Valores aceitos: {', '.join(sorted(roles_validos))}")
        return v
