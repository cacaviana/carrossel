"""Testes unitarios para SlideTextoPronto DTO e CriarPipelineRequest.

Testa:
- SlideTextoPronto aceita tipo_layout opcional
- tipo_layout None por default
- CriarPipelineRequest com slides_texto_pronto e tipo_layout
- Validacao de max_slides
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dtos.pipeline.criar_pipeline.request import SlideTextoPronto, CriarPipelineRequest


class TestSlideTextoProntoDTO:
    def test_campos_obrigatorios(self):
        s = SlideTextoPronto(principal="Titulo do slide")
        assert s.principal == "Titulo do slide"
        assert s.alternativo == ""

    def test_tipo_layout_default_none(self):
        s = SlideTextoPronto(principal="Titulo")
        assert s.tipo_layout is None

    def test_tipo_layout_texto(self):
        s = SlideTextoPronto(principal="Titulo", tipo_layout="texto")
        assert s.tipo_layout == "texto"

    def test_tipo_layout_lista(self):
        s = SlideTextoPronto(principal="Titulo", tipo_layout="lista")
        assert s.tipo_layout == "lista"

    def test_tipo_layout_comparativo(self):
        s = SlideTextoPronto(principal="Titulo", tipo_layout="comparativo")
        assert s.tipo_layout == "comparativo"

    def test_tipo_layout_dados(self):
        s = SlideTextoPronto(principal="Titulo", tipo_layout="dados")
        assert s.tipo_layout == "dados"

    def test_alternativo_opcional(self):
        s = SlideTextoPronto(principal="X", alternativo="corpo do slide")
        assert s.alternativo == "corpo do slide"


class TestCriarPipelineRequestComTipoLayout:
    def test_slides_texto_pronto_com_tipo_layout(self):
        req = CriarPipelineRequest(
            tema="Titulo do post",
            modo_entrada="texto_pronto",
            slides_texto_pronto=[
                SlideTextoPronto(principal="Slide 1", tipo_layout="texto"),
                SlideTextoPronto(principal="Slide 2", tipo_layout="lista"),
                SlideTextoPronto(principal="Slide 3", tipo_layout="dados"),
            ],
        )
        assert len(req.slides_texto_pronto) == 3
        assert req.slides_texto_pronto[0].tipo_layout == "texto"
        assert req.slides_texto_pronto[1].tipo_layout == "lista"
        assert req.slides_texto_pronto[2].tipo_layout == "dados"

    def test_slides_texto_pronto_sem_tipo_layout(self):
        req = CriarPipelineRequest(
            tema="Titulo do post",
            modo_entrada="texto_pronto",
            slides_texto_pronto=[
                SlideTextoPronto(principal="Slide 1"),
            ],
        )
        assert req.slides_texto_pronto[0].tipo_layout is None

    def test_max_slides_ideia_validos(self):
        for n in (3, 4, 5):
            req = CriarPipelineRequest(tema="Tema", modo_entrada="ideia", max_slides=n)
            assert req.max_slides == n

    def test_max_slides_ideia_invalido(self):
        with pytest.raises(ValueError, match="aceita apenas 3, 4 ou 5"):
            CriarPipelineRequest(tema="Tema", modo_entrada="ideia", max_slides=10)

    def test_max_slides_texto_pronto_valido(self):
        req = CriarPipelineRequest(tema="Tema", modo_entrada="texto_pronto", max_slides=7)
        assert req.max_slides == 7

    def test_max_slides_texto_pronto_invalido(self):
        with pytest.raises(ValueError, match="ate 7 slides"):
            CriarPipelineRequest(tema="Tema", modo_entrada="texto_pronto", max_slides=8)

    def test_tema_strip(self):
        """Validator agora so faz strip, nao valida tamanho minimo."""
        req = CriarPipelineRequest(tema="  ok  ")
        assert req.tema == "ok"
