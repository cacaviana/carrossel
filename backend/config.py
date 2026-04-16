from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MSSQL_URL: str = ""
    CLAUDE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_DRIVE_CREDENTIALS: str = ""
    GOOGLE_DRIVE_FOLDER_ID: str = ""
    TENANT_ID: str = "itvalley"
    MONGO_URL: str = ""
    jwt_secret_key: str = ""
    default_tenant_id: str = "itvalley"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
