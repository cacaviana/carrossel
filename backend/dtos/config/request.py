from pydantic import BaseModel


class SaveConfigRequest(BaseModel):
    claude_api_key: str | None = None
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    google_drive_credentials: str | None = None
    google_drive_folder_id: str | None = None
