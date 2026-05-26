from pydantic import BaseModel, field_validator, model_validator
from typing import Optional


class SlideTextoPronto(BaseModel):
    principal: str
    alternativo: str = ""
    tipo_layout: Optional[str] = None


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
    background_base64: Optional[str] = None  # imagem de fundo (base64) — modo upload
    template_layout: Optional[str] = None  # template escolhido — modo upload
    cta: Optional[str] = None  # CTA do anuncio (max 30 chars). So usado quando formato=anuncio.

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
        # Validacao modo upload: exige background e template
        if self.modo_entrada == "upload":
            if not self.background_base64:
                raise ValueError(
                    "Modo 'upload' requer 'background_base64' (imagem de fundo em base64)"
                )
            if not self.template_layout:
                raise ValueError(
                    "Modo 'upload' requer 'template_layout' (template de layout escolhido)"
                )
            valid_templates = (
                "texto_centralizado",
                "texto_no_topo",
                "texto_embaixo",
                "criativo_topo",
                "criativo_embaixo",
                "criativo",  # alias de compatibilidade (= criativo_topo)
            )
            if self.template_layout not in valid_templates:
                raise ValueError(
                    f"template_layout invalido: '{self.template_layout}'. "
                    f"Valores aceitos: {', '.join(valid_templates)}"
                )

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
