from pydantic import BaseModel
from typing import Optional


class ColunaBase(BaseModel):
    id: str
    name: str
    order: int
    color: Optional[str] = None


class BoardBase(BaseModel):
    name: str
