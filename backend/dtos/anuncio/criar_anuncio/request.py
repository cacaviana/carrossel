from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CriarAnuncioRequest(BaseModel):
    """Request pra criar anuncio + disparar pipeline."""
    titulo: str = Field(min_length=3, max_length=200)
    tema_ou_briefing: str = Field(default="", max_length=5000)
    modo_entrada: str = "texto"                   # "texto" | "disciplina"
    disciplina: Optional[str] = None
    tecnologia: Optional[str] = None
    etapa_funil: Optional[str] = "avulso"         # topo|meio|fundo|avulso
    pipeline_funil_id: Optional[str] = None
    foto_criador_id: Optional[str] = None
    brand_slug: Optional[str] = None
    formato: Optional[str] = "anuncio"            # aceito para compat mas fixo

    # Copy (modo texto_pronto usa; modo ideia deixa vazio)
    headline: Optional[str] = Field(default=None, max_length=40)
    descricao: Optional[str] = Field(default=None, max_length=125)
    cta: Optional[str] = Field(default=None, max_length=30)

    @field_validator("modo_entrada")
    @classmethod
    def modo_valido(cls, v: str) -> str:
        if v not in {"texto", "disciplina", "texto_pronto", "ideia"}:
            raise ValueError("modo_entrada invalido")
        return v

    @field_validator("etapa_funil")
    @classmethod
    def etapa_valida(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return "avulso"
        if v not in {"topo", "meio", "fundo", "avulso"}:
            raise ValueError(f"etapa_funil invalida: {v}")
        return v
