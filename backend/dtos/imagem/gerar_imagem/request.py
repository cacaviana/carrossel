from pydantic import BaseModel


class SlideInput(BaseModel):
    type: str
    headline: str | None = None
    subline: str | None = None
    title: str | None = None
    bullets: list[str] | None = None
    etapa: str | None = None
    code: str | None = None
    caption: str | None = None
    left_label: str | None = None
    left_items: list[str] | None = None
    right_label: str | None = None
    right_items: list[str] | None = None
    tags: list[str] | None = None


class GerarImagemRequest(BaseModel):
    slides: list[SlideInput]
    foto_criador: str | None = None
    design_system: str | None = None


class GerarImagemSlideRequest(BaseModel):
    slide: SlideInput
    slide_index: int
    total_slides: int
    foto_criador: str | None = None
    design_system: str | None = None
