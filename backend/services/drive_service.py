import asyncio
import base64
import json
import tempfile
from datetime import datetime
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaInMemoryUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]


def _build_service(credentials_json: str):
    creds_data = json.loads(credentials_json)
    credentials = service_account.Credentials.from_service_account_info(
        creds_data, scopes=SCOPES
    )
    return build("drive", "v3", credentials=credentials)


def _create_folder_sync(service, name: str, parent_id: str | None = None) -> str:
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        metadata["parents"] = [parent_id]
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder.get("id")


def _upload_bytes_sync(
    service,
    file_bytes: bytes,
    file_name: str,
    mime_type: str,
    folder_id: str,
) -> dict:
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_name).suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    file_metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaFileUpload(tmp_path, mimetype=mime_type, resumable=True)
    file = service.files().create(
        body=file_metadata, media_body=media, fields="id, webViewLink"
    ).execute()
    Path(tmp_path).unlink(missing_ok=True)
    return {"file_id": file.get("id"), "web_view_link": file.get("webViewLink", "")}


def _list_folders_sync(credentials_json: str) -> list[dict]:
    service = _build_service(credentials_json)
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)",
        pageSize=50,
        orderBy="name",
    ).execute()
    return results.get("files", [])


def _save_carrossel_sync(
    credentials_json: str,
    parent_folder_id: str,
    title: str,
    pdf_base64: str | None,
    images_base64: list[str | None],
) -> dict:
    service = _build_service(credentials_json)

    # Cria subpasta: "{title} - {YYYY-MM-DD}"
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    subfolder_name = f"{title} - {data_hoje}"
    subfolder_id = _create_folder_sync(service, subfolder_name, parent_folder_id)

    # Faz a pasta pública para que webViewLink funcione
    service.permissions().create(
        fileId=subfolder_id,
        body={"role": "reader", "type": "anyone"},
    ).execute()

    # Gera PDF das imagens se nao foi fornecido
    if not pdf_base64 and images_base64:
        from services.pdf_service import gerar_pdf_from_images
        pdf_base64 = gerar_pdf_from_images(images_base64)

    # Upload do PDF
    pdf_result = {"web_view_link": ""}
    if pdf_base64:
        pdf_bytes = base64.b64decode(pdf_base64)
        pdf_result = _upload_bytes_sync(
            service, pdf_bytes, f"{title}.pdf", "application/pdf", subfolder_id
        )

    # Upload de cada imagem PNG
    for i, img_b64 in enumerate(images_base64):
        if not img_b64:
            continue
        # Remove prefixo data:image/png;base64, se presente
        if "," in img_b64:
            img_b64 = img_b64.split(",", 1)[1]
        img_bytes = base64.b64decode(img_b64)
        _upload_bytes_sync(
            service,
            img_bytes,
            f"slide-{i + 1:02d}.png",
            "image/png",
            subfolder_id,
        )

    folder_link = f"https://drive.google.com/drive/folders/{subfolder_id}"
    return {
        "subfolder_id": subfolder_id,
        "subfolder_name": subfolder_name,
        "web_view_link": pdf_result.get("web_view_link") or folder_link,
    }


def _list_files_in_folder_sync(credentials_json: str, folder_id: str) -> list[dict]:
    service = _build_service(credentials_json)
    results = service.files().list(
        q=f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)",
        pageSize=50,
        orderBy="name",
    ).execute()
    return results.get("files", [])


def _download_file_content_sync(credentials_json: str, file_id: str) -> dict:
    service = _build_service(credentials_json)
    file_meta = service.files().get(fileId=file_id, fields="id, name").execute()
    content = service.files().get_media(fileId=file_id).execute()
    return {
        "id": file_meta.get("id"),
        "name": file_meta.get("name"),
        "content": content.decode("utf-8") if isinstance(content, bytes) else str(content),
    }


# ── API pública (async wrappers) ──────────────────────────────────────────────

async def upload_to_drive(
    file_base64: str,
    file_name: str,
    mime_type: str,
    credentials_json: str,
    folder_id: str | None = None,
) -> dict:
    service = _build_service(credentials_json)
    file_bytes = base64.b64decode(file_base64)
    folder = folder_id or ""
    return await asyncio.get_event_loop().run_in_executor(
        None, _upload_bytes_sync, service, file_bytes, file_name, mime_type, folder
    )


async def list_folders(credentials_json: str) -> list[dict]:
    return await asyncio.get_event_loop().run_in_executor(
        None, _list_folders_sync, credentials_json
    )


async def list_files_in_folder(credentials_json: str, folder_id: str) -> list[dict]:
    return await asyncio.get_event_loop().run_in_executor(
        None, _list_files_in_folder_sync, credentials_json, folder_id
    )


async def download_file_content(credentials_json: str, file_id: str) -> dict:
    return await asyncio.get_event_loop().run_in_executor(
        None, _download_file_content_sync, credentials_json, file_id
    )


async def delete_file(credentials_json: str, file_id: str):
    def _delete_sync():
        service = _build_service(credentials_json)
        service.files().delete(fileId=file_id).execute()
    await asyncio.get_event_loop().run_in_executor(None, _delete_sync)


async def save_carrossel(
    credentials_json: str,
    parent_folder_id: str,
    title: str,
    pdf_base64: str | None,
    images_base64: list[str | None],
) -> dict:
    return await asyncio.get_event_loop().run_in_executor(
        None,
        _save_carrossel_sync,
        credentials_json,
        parent_folder_id,
        title,
        pdf_base64,
        images_base64,
    )
