from pydantic import BaseModel


class UploadDriveResponse(BaseModel):
    file_id: str
    web_view_link: str


class SaveCarrosselDriveResponse(BaseModel):
    subfolder_name: str
    web_view_link: str


class PastaResponse(BaseModel):
    id: str
    name: str
