"""Testes unitarios — DTOs do dominio Imagem (GerarImagemRequest, SlideInput, Responses).

Cobertos nos 3 formatos: post_unico, capa_reels, thumbnail_youtube.
Valida: Literal FormatoValido, defaults, campos obrigatorios, parametrizacao por formato.
"""

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dtos.imagem.gerar_imagem.request import (
    GerarImagemRequest,
    GerarImagemSlideRequest,
    SlideInput,
)
from dtos.imagem.gerar_imagem.response import (
    GerarImagemResponse,
    GerarImagemSlideResponse,
)


# =============================================================================
# SlideInput — fields compartilhados pelos 3 formatos
# =============================================================================
class TestSlideInput:
    def test_cria_minimo_com_type(self):
        s = SlideInput(type="cover")
        assert s.type == "cover"
        assert s.headline is None

    def test_rejeita_sem_type(self):
        with pytest.raises(ValidationError):
            SlideInput()

    def test_aceita_todos_campos(self):
        s = SlideInput(
            type="cover",
            headline="H",
            subline="S",
            title="T",
            bullets=["a", "b"],
            etapa="HOOK",
            code="print(1)",
            caption="cap",
            left_label="L", left_items=["l1"],
            right_label="R", right_items=["r1"],
            tags=["tag1"],
            illustration_description="desc",
        )
        assert s.bullets == ["a", "b"]
        assert s.illustration_description == "desc"

    def test_model_dump_contem_so_campos_esperados(self):
        s = SlideInput(type="cover", headline="H")
        dump = s.model_dump()
        # Campos presentes
        assert "type" in dump
        assert "headline" in dump
        # Sem campos estranhos
        assert "pipeline_id" not in dump


# =============================================================================
# GerarImagemRequest
# =============================================================================
class TestGerarImagemRequest:
    def _slide(self):
        return SlideInput(type="cover", headline="H")

    def test_defaults(self):
        req = GerarImagemRequest(slides=[self._slide()])
        assert req.formato == "carrossel"
        assert req.avatar_mode == "livre"
        assert req.skip_validation is False
        assert req.foto_criador is None
        assert req.brand_slug is None
        assert req.instrucao_extra is None

    def test_rejeita_sem_slides(self):
        with pytest.raises(ValidationError):
            GerarImagemRequest()

    def test_aceita_slides_vazios(self):
        """Lista vazia e tecnicamente valida pelo DTO — a regra de negocio
        de 'pelo menos 1 slide' fica no Service/Factory."""
        req = GerarImagemRequest(slides=[])
        assert req.slides == []

    @pytest.mark.parametrize("formato", ["carrossel", "post_unico", "thumbnail_youtube", "capa_reels"])
    def test_aceita_formatos_validos(self, formato):
        req = GerarImagemRequest(slides=[self._slide()], formato=formato)
        assert req.formato == formato

    def test_rejeita_formato_invalido(self):
        with pytest.raises(ValidationError):
            GerarImagemRequest(slides=[self._slide()], formato="banner_linkedin")

    @pytest.mark.parametrize("avatar_mode", ["capa", "livre", "sem", "sim"])
    def test_aceita_avatar_modes(self, avatar_mode):
        # avatar_mode e str livre no DTO (sem Literal) — qualquer string passa
        req = GerarImagemRequest(slides=[self._slide()], avatar_mode=avatar_mode)
        assert req.avatar_mode == avatar_mode


# =============================================================================
# GerarImagemSlideRequest
# =============================================================================
class TestGerarImagemSlideRequest:
    def test_campos_obrigatorios(self):
        req = GerarImagemSlideRequest(
            slide=SlideInput(type="cover"),
            slide_index=0,
            total_slides=1,
        )
        assert req.slide_index == 0
        assert req.total_slides == 1
        assert req.formato == "carrossel"

    def test_rejeita_sem_slide_index(self):
        with pytest.raises(ValidationError):
            GerarImagemSlideRequest(
                slide=SlideInput(type="cover"),
                total_slides=1,
            )

    @pytest.mark.parametrize("formato,total_slides", [
        ("post_unico", 1),
        ("capa_reels", 1),
        ("thumbnail_youtube", 1),
    ])
    def test_cria_para_cada_formato(self, formato, total_slides):
        req = GerarImagemSlideRequest(
            slide=SlideInput(type="cover"),
            slide_index=0,
            total_slides=total_slides,
            formato=formato,
        )
        assert req.formato == formato

    def test_rejeita_formato_invalido(self):
        with pytest.raises(ValidationError):
            GerarImagemSlideRequest(
                slide=SlideInput(type="cover"),
                slide_index=0,
                total_slides=1,
                formato="story_tiktok",
            )


# =============================================================================
# Responses
# =============================================================================
class TestGerarImagemResponse:
    def test_aceita_lista_de_base64(self):
        resp = GerarImagemResponse(images=["data:image/png;base64,AAA", None])
        assert len(resp.images) == 2
        assert resp.images[1] is None

    def test_aceita_lista_vazia(self):
        resp = GerarImagemResponse(images=[])
        assert resp.images == []


class TestGerarImagemSlideResponse:
    def test_aceita_imagem(self):
        resp = GerarImagemSlideResponse(image="data:image/png;base64,AAA")
        assert resp.image.startswith("data:")

    def test_aceita_none(self):
        resp = GerarImagemSlideResponse(image=None)
        assert resp.image is None
