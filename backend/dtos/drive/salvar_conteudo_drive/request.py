from pydantic import BaseModel
from typing import Optional


class SalvarConteudoDriveRequest(BaseModel):
    pipeline_id: str
    titulo: str
    formato: str
    pdf_base64: Optional[str] = None
    images_base64: list[str | None]
