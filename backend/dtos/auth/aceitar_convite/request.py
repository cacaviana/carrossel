"""Request para aceitar convite e definir senha."""

import re

from pydantic import BaseModel, field_validator


class AceitarConviteRequest(BaseModel):
    token: str
    password: str

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
