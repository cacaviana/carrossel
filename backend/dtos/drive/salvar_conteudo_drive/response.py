from pydantic import BaseModel


class SalvarConteudoDriveResponse(BaseModel):
    subfolder_name: str
    web_view_link: str
    total_arquivos: int
