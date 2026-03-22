"""Mapper de conteúdo — dict ↔ DTOs."""

from dtos.conteudo.gerar_conteudo.response import GerarConteudoResponse
from dtos.conteudo.base import SlideResponse


def dict_to_response(data: dict) -> GerarConteudoResponse:
    """Converte dict retornado pelo Claude em GerarConteudoResponse."""
    slides = [SlideResponse(**s) for s in data.get("slides", [])]
    return GerarConteudoResponse(
        title=data.get("title", ""),
        disciplina=data.get("disciplina", ""),
        tecnologia_principal=data.get("tecnologia_principal", ""),
        hook_formula=data.get("hook_formula", ""),
        slides=slides,
        legenda_linkedin=data.get("legenda_linkedin", ""),
    )
