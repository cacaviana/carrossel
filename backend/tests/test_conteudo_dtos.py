"""Testes unitarios — DTOs do dominio Conteudo (GerarConteudoRequest/Response).

Cobertos nos 3 formatos (PostUnico, Reels, Thumbnail) + carrossel (pai).
Todos os 3 formatos compartilham o mesmo DTO — a diferenca e apenas os valores
dos campos total_slides / tipo_carrossel.
"""

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dtos.conteudo.gerar_conteudo.request import GerarConteudoRequest
from dtos.conteudo.gerar_conteudo.response import GerarConteudoResponse
from dtos.conteudo.base import SlideResponse


# =============================================================================
# GerarConteudoRequest
# =============================================================================
class TestGerarConteudoRequest:
    def test_aceita_request_vazio_com_defaults(self):
        req = GerarConteudoRequest()
        assert req.total_slides == 10
        assert req.tipo_carrossel == "texto"
        assert req.disciplina is None
        assert req.tecnologia is None
        assert req.tema_custom is None
        assert req.texto_livre is None

    def test_aceita_todos_os_campos(self):
        req = GerarConteudoRequest(
            disciplina="D5",
            tecnologia="Transfer Learning",
            tema_custom="fine-tuning",
            total_slides=7,
            tipo_carrossel="visual",
        )
        assert req.disciplina == "D5"
        assert req.total_slides == 7

    def test_aceita_texto_livre(self):
        req = GerarConteudoRequest(
            texto_livre="Minha thread sobre XGBoost",
            total_slides=3,
        )
        assert req.texto_livre == "Minha thread sobre XGBoost"
        assert req.total_slides == 3

    @pytest.mark.parametrize("tipo", ["texto", "visual", "infografico"])
    def test_aceita_tipos_carrossel_validos(self, tipo):
        req = GerarConteudoRequest(tipo_carrossel=tipo)
        assert req.tipo_carrossel == tipo


# =============================================================================
# SlideResponse (base compartilhada pros 3 formatos)
# =============================================================================
class TestSlideResponse:
    def test_cria_slide_minimo_com_type(self):
        s = SlideResponse(type="cover")
        assert s.type == "cover"
        assert s.headline is None

    def test_rejeita_sem_type(self):
        with pytest.raises(ValidationError):
            SlideResponse()

    def test_aceita_slide_cover_completo(self):
        s = SlideResponse(
            type="cover",
            tipo_layout="texto",
            headline="Como usar YOLO",
            subline="Deteccao em tempo real",
            title="YOLO v8",
        )
        assert s.headline == "Como usar YOLO"
        assert s.tipo_layout == "texto"

    def test_aceita_slide_content_com_bullets(self):
        s = SlideResponse(
            type="content",
            bullets=["bullet 1", "bullet 2", "bullet 3"],
        )
        assert len(s.bullets) == 3

    def test_aceita_slide_comparativo(self):
        s = SlideResponse(
            type="comparison",
            tipo_layout="comparativo",
            left_label="Antes",
            left_items=["lento", "manual"],
            right_label="Depois",
            right_items=["rapido", "automatico"],
        )
        assert s.left_label == "Antes"
        assert len(s.right_items) == 2

    def test_aceita_slide_code(self):
        s = SlideResponse(
            type="content",
            code="print('hello')",
            caption="Exemplo Python",
        )
        assert "print" in s.code

    def test_aceita_slide_com_illustration_description(self):
        s = SlideResponse(
            type="infographic",
            illustration_description="Diagrama com 3 caixas conectadas",
        )
        assert "caixas" in s.illustration_description


# =============================================================================
# GerarConteudoResponse
# =============================================================================
class TestGerarConteudoResponse:
    def test_cria_response_com_campos_obrigatorios(self):
        resp = GerarConteudoResponse(
            title="YOLO para iniciantes",
            disciplina="D1",
            tecnologia_principal="YOLO",
            hook_formula="problema-agitacao-solucao",
            slides=[SlideResponse(type="cover", headline="Teste")],
            legenda_linkedin="Legenda curta",
        )
        assert resp.title == "YOLO para iniciantes"
        assert len(resp.slides) == 1

    def test_rejeita_sem_title(self):
        with pytest.raises(ValidationError):
            GerarConteudoResponse(
                disciplina="D1",
                tecnologia_principal="YOLO",
                hook_formula="x",
                slides=[],
                legenda_linkedin="",
            )

    def test_rejeita_sem_slides(self):
        with pytest.raises(ValidationError):
            GerarConteudoResponse(
                title="t",
                disciplina="D1",
                tecnologia_principal="YOLO",
                hook_formula="x",
                legenda_linkedin="",
            )

    def test_aceita_slides_vazios(self):
        """Lista vazia e tecnicamente valida (tipo list[SlideResponse])."""
        resp = GerarConteudoResponse(
            title="t",
            disciplina="D1",
            tecnologia_principal="YOLO",
            hook_formula="x",
            slides=[],
            legenda_linkedin="",
        )
        assert resp.slides == []


# =============================================================================
# Parametrizacao por formato — o DTO e UNICO pros 3 formatos
# =============================================================================
@pytest.mark.parametrize("formato,total_slides,tipo", [
    ("post_unico", 1, "infografico"),
    ("capa_reels", 1, "visual"),
    ("thumbnail_youtube", 1, "visual"),
])
class TestRequestPorFormato:
    """Valida que o mesmo DTO aceita configs dos 3 novos formatos."""

    def test_cria_request_para_formato(self, formato, total_slides, tipo):
        req = GerarConteudoRequest(
            disciplina="D7",
            tecnologia="RAG",
            total_slides=total_slides,
            tipo_carrossel=tipo,
        )
        assert req.total_slides == total_slides
        assert req.tipo_carrossel == tipo
