from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CardResponse(BaseModel):
    id: str
    board_id: str
    column_id: str
    title: str
    copy_text: Optional[str] = None
    disciplina: Optional[str] = None
    tecnologia: Optional[str] = None
    priority: str
    assigned_user_ids: list[str] = []
    created_by: str
    pipeline_id: Optional[str] = None
    drive_link: Optional[str] = None
    drive_folder_name: Optional[str] = None
    pdf_url: Optional[str] = None
    image_urls: list[str] = []
    order_in_column: int = 0
    comment_count: int = 0
    deadline: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
