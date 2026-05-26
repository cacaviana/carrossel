from pydantic import BaseModel, field_validator


class CriarComentarioRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def texto_nao_vazio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Comentario nao pode ser vazio")
        return v.strip()
