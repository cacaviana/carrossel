from typing import Optional
from pydantic import BaseModel


class ExportarAnuncioResponse(BaseModel):
    destino: str
    drive_folder_id: Optional[str] = None
    drive_folder_link: Optional[str] = None
    # Quando destino=png, retornamos a imagem em base64 (data URI friendly)
    image_base64: Optional[str] = None
    arquivos_exportados: list[str] = []
    warning: Optional[str] = None
