from pydantic import BaseModel
from typing import Optional


class VincularArtefatoRequest(BaseModel):
    drive_link: Optional[str] = None
    drive_folder_name: Optional[str] = None
    pdf_url: Optional[str] = None
    image_urls: Optional[list[str]] = None
