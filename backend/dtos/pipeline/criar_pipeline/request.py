from pydantic import BaseModel, field_validator, model_validator
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

    @model_validator(mode="after")
    def validar_max_slides(self):
        """Fase 5:
        - modo 'ideia' aceita 3, 4 ou 5 slides
        - modo 'texto_pronto' aceita ate 7 slides
        - outros modos: sem restricao explicita
        """
        if self.max_slides is None:
            return self
        if self.modo_entrada == "ideia":
            if self.max_slides not in (3, 4, 5):
                raise ValueError(
                    f"Modo 'ideia' aceita apenas 3, 4 ou 5 slides (recebido {self.max_slides})"
                )
        elif self.modo_entrada == "texto_pronto":
            if self.max_slides > 7 or self.max_slides < 1:
                raise ValueError(
                    f"Modo 'texto_pronto' aceita ate 7 slides (recebido {self.max_slides})"
                )
        return self

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
