from pydantic import BaseModel, field_validator
from typing import Optional


class SlideTextoPronto(BaseModel):
    principal: str
    alternativo: str = ""


class CriarPipelineRequest(BaseModel):
    tema: str
    formato: Optional[str] = None
    formatos: Optional[list[str]] = None
    modo_funil: bool = False
    modo_entrada: str = "ideia"
    disciplina: Optional[str] = None
    tecnologia: Optional[str] = None
    foto_criador: Optional[str] = None
    foto_criador_id: Optional[str] = None
    slides_texto_pronto: Optional[list[SlideTextoPronto]] = None
    brand_slug: Optional[str] = None
    avatar_mode: Optional[str] = "livre"  # capa, livre, sem, sim
    max_slides: Optional[int] = None  # maximo de slides para ideia livre

    @field_validator("tema")
    @classmethod
    def tema_minimo(cls, v: str, info) -> str:
        # Texto pronto usa slides individuais, tema pode ser curto
        return v.strip()

    def get_formato(self) -> str:
        if self.formato:
            return self.formato
        if self.formatos and len(self.formatos) > 0:
            return self.formatos[0]
        return "carrossel"

    def get_formatos(self) -> list[str]:
        if self.formatos:
            return self.formatos
        if self.formato:
            return [self.formato]
        return ["carrossel"]
