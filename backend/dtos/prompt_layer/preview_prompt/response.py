from pydantic import BaseModel


class CamadaPreview(BaseModel):
    nome: str
    conteudo: str
    chars: int


class PreviewPromptResponse(BaseModel):
    prompt_final: str
    camadas: list[CamadaPreview]
    total_caracteres: int
    modelo_selecionado: str | None = None
