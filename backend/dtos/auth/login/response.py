"""Response de login com JWT e dados do usuario."""

from pydantic import BaseModel


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    tenant_id: str
    role: str
    name: str
    email: str
