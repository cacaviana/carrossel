import os

from fastapi import APIRouter

from dtos.config.request import SaveConfigRequest
from dtos.config.response import ConfigStatusResponse
from factories.config_factory import read_env, write_env, update_key

router = APIRouter()


@router.post("/config")
async def salvar_config(req: SaveConfigRequest) -> dict:
    env = read_env()
    update_key(env, "CLAUDE_API_KEY", req.claude_api_key)
    update_key(env, "OPENAI_API_KEY", req.openai_api_key)
    update_key(env, "GEMINI_API_KEY", req.gemini_api_key)
    update_key(env, "GOOGLE_DRIVE_CREDENTIALS", req.google_drive_credentials)
    update_key(env, "GOOGLE_DRIVE_FOLDER_ID", req.google_drive_folder_id)
    write_env(env)
    return {"ok": True}


@router.get("/config", response_model=ConfigStatusResponse)
async def status_config() -> ConfigStatusResponse:
    return ConfigStatusResponse(
        claude_api_key_set=bool(os.getenv("CLAUDE_API_KEY")),
        openai_api_key_set=bool(os.getenv("OPENAI_API_KEY")),
        gemini_api_key_set=bool(os.getenv("GEMINI_API_KEY")),
        google_drive_credentials_set=bool(os.getenv("GOOGLE_DRIVE_CREDENTIALS")),
        google_drive_folder_id=os.getenv("GOOGLE_DRIVE_FOLDER_ID", ""),
    )
