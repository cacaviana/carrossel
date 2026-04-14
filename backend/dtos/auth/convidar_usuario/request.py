"""Request de convite de usuario (admin convida por email)."""

from pydantic import BaseModel, EmailStr, field_validator


class ConvidarUsuarioRequest(BaseModel):
    email: EmailStr
    name: str
    role: str = "viewer"

    @field_validator("role")
    @classmethod
    def role_valido(cls, v: str) -> str:
        roles_validos = {"admin", "copywriter", "designer", "reviewer", "viewer"}
        if v not in roles_validos:
            raise ValueError(f"Role invalido. Valores aceitos: {', '.join(sorted(roles_validos))}")
        return v
