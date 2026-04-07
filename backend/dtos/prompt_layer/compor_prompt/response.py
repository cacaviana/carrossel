from pydantic import BaseModel


class ComporPromptResponse(BaseModel):
    prompt_final: str
    camadas_usadas: list[str]
    modelo_sugerido: str | None = None
    total_caracteres: int
