import os

from fastapi import APIRouter, HTTPException

from dtos.drive.salvar_drive.request import UploadDriveRequest, SaveCarrosselDriveRequest
from dtos.drive.salvar_drive.response import UploadDriveResponse, SaveCarrosselDriveResponse, PastaResponse
from services.drive_service import upload_to_drive, list_folders, save_carrossel

router = APIRouter()


def _get_credentials() -> str:
    creds = os.getenv("GOOGLE_DRIVE_CREDENTIALS")
    if not creds:
        raise HTTPException(
            status_code=400,
            detail="GOOGLE_DRIVE_CREDENTIALS não configurada. Acesse /configuracoes.",
        )
    return creds


def _get_folder_id() -> str:
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id:
        raise HTTPException(
            status_code=400,
            detail="Pasta do Google Drive não configurada. Acesse /configuracoes.",
        )
    return folder_id


@router.get("/drive/pastas", response_model=list[PastaResponse])
async def api_listar_pastas():
    credentials_json = _get_credentials()
    try:
        pastas = await list_folders(credentials_json)
        return pastas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/google-drive/carrossel", response_model=SaveCarrosselDriveResponse)
async def api_salvar_carrossel(req: SaveCarrosselDriveRequest):
    credentials_json = _get_credentials()
    folder_id = _get_folder_id()
    try:
        result = await save_carrossel(
            credentials_json=credentials_json,
            parent_folder_id=folder_id,
            title=req.title,
            pdf_base64=req.pdf_base64,
            images_base64=req.images_base64,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/google-drive", response_model=UploadDriveResponse)
async def api_upload_drive(req: UploadDriveRequest):
    credentials_json = _get_credentials()
    try:
        result = await upload_to_drive(
            file_base64=req.file_base64,
            file_name=req.file_name,
            mime_type=req.mime_type,
            credentials_json=credentials_json,
            folder_id=req.folder_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
