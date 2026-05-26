from pydantic import BaseModel, Field


class ListarCalendarioRequest(BaseModel):
    """Mes no formato YYYY-MM. Cards com deadline dentro do mes sao retornados."""
    mes: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="Ano-mes (ex: 2026-04)")
