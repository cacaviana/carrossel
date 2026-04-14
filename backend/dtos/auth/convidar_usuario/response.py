"""Response apos criar convite."""

from pydantic import BaseModel
from datetime import datetime


class ConviteResponse(BaseModel):
    invite_token: str
    email: str
    name: str
    role: str
    expires_at: datetime
    invite_url: str
