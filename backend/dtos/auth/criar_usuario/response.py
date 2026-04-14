"""Response apos criar usuario."""

from pydantic import BaseModel
from datetime import datetime


class UsuarioResponse(BaseModel):
    user_id: str
    tenant_id: str
    email: str
    name: str
    role: str
    avatar_url: str | None = None
    created_at: datetime
