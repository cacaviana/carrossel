from pydantic import BaseModel


class SlideResponse(BaseModel):
    type: str
    tipo_layout: str | None = None
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
    illustration_description: str | None = None
