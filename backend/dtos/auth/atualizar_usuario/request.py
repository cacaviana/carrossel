"""Request para atualizar dados de um usuario (admin only)."""

from pydantic import BaseModel, field_validator


class AtualizarUsuarioRequest(BaseModel):
    name: str | None = None
    role: str | None = None
    avatar_url: str | None = None

    @field_validator("role")
    @classmethod
    def role_valido(cls, v: str | None) -> str | None:
        if v is None:
            return v
        roles_validos = {"admin", "copywriter", "designer", "reviewer", "viewer"}
        if v not in roles_validos:
            raise ValueError(f"Role invalido. Valores aceitos: {', '.join(sorted(roles_validos))}")
        return v
