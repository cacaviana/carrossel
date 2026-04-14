"""Response de /me — dados do usuario autenticado."""

from pydantic import BaseModel
from datetime import datetime


class MeResponse(BaseModel):
    user_id: str
    tenant_id: str
    role: str
    email: str
    name: str
    avatar_url: str | None = None
    created_at: datetime | None = None
