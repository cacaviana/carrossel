from pydantic import BaseModel


class UploadDriveRequest(BaseModel):
    file_base64: str
    file_name: str
    mime_type: str = "application/pdf"
    folder_id: str | None = None


class SaveCarrosselDriveRequest(BaseModel):
    title: str
    pdf_base64: str | None = None
    images_base64: list[str | None]
