from pydantic import BaseModel


class MetricItem(BaseModel):
    label: str
    value: str


class TableData(BaseModel):
    headers: list[str]
    rows: list[list[str]]


class SlideResponse(BaseModel):
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
    metrics: list[MetricItem] | None = None
    table: TableData | None = None
