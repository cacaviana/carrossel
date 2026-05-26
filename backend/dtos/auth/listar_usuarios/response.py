"""Response de listagem de usuarios do tenant."""

from pydantic import BaseModel
from datetime import datetime


class UsuarioItem(BaseModel):
    user_id: str
    email: str
    name: str
    role: str
    avatar_url: str | None = None
    created_at: datetime
    deleted_at: datetime | None = None


class ListarUsuariosResponse(BaseModel):
    usuarios: list[UsuarioItem]
    total: int
