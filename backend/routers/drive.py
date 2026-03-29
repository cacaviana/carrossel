import os

from fastapi import APIRouter, HTTPException

from dtos.drive.salvar_drive.request import UploadDriveRequest, SaveCarrosselDriveRequest
from dtos.drive.salvar_drive.response import UploadDriveResponse, SaveCarrosselDriveResponse, PastaResponse
from services.drive_service import upload_to_drive, list_folders, save_carrossel, list_files_in_folder, download_file_content
from services.db_service import salvar_historico

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


@router.get("/drive/design-systems")
async def api_listar_design_systems():
    credentials_json = _get_credentials()
    folder_id = os.getenv("DESIGN_SYSTEMS_FOLDER_ID")
    if not folder_id:
        return []
    try:
        files = await list_files_in_folder(credentials_json, folder_id)
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drive/design-systems/{file_id}")
async def api_get_design_system(file_id: str):
    credentials_json = _get_credentials()
    try:
        result = await download_file_content(credentials_json, file_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drive/design-systems")
async def api_upload_design_system(req: UploadDriveRequest):
    credentials_json = _get_credentials()
    folder_id = os.getenv("DESIGN_SYSTEMS_FOLDER_ID")
    if not folder_id:
        raise HTTPException(status_code=400, detail="DESIGN_SYSTEMS_FOLDER_ID não configurada.")
    try:
        result = await upload_to_drive(
            file_base64=req.file_base64,
            file_name=req.file_name,
            mime_type=req.mime_type,
            credentials_json=credentials_json,
            folder_id=folder_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/drive/design-systems/{file_id}")
async def api_delete_design_system(file_id: str):
    credentials_json = _get_credentials()
    try:
        from services.drive_service import delete_file
        await delete_file(credentials_json, file_id)
        return {"ok": True}
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
        # Salvar no banco de dados
        try:
            await salvar_historico(
                titulo=req.title,
                disciplina=req.disciplina,
                tecnologia=req.tecnologia_principal,
                tipo=req.tipo_carrossel or "texto",
                total_slides=len([i for i in req.images_base64 if i]),
                legenda=req.legenda_linkedin,
                drive_link=result.get("web_view_link", ""),
                folder_name=result.get("subfolder_name", ""),
            )
        except Exception:
            pass  # Não falhar o save no Drive por causa do banco
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
