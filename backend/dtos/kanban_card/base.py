from pydantic import BaseModel
from typing import Optional


class CardBase(BaseModel):
    title: str
    copy_text: Optional[str] = None
    disciplina: Optional[str] = None
    tecnologia: Optional[str] = None
    priority: str = "media"
