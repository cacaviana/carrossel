from pydantic import BaseModel


class ConfigStatusResponse(BaseModel):
    claude_api_key_set: bool
    gemini_api_key_set: bool
    google_drive_credentials_set: bool
    google_drive_folder_id: str
