"""Testes unitarios — Routers que CRIAM artefatos para os 3 formatos.

Cobre os casos de uso:
 - Criar PostUnico (via /api/gerar-conteudo + /api/gerar-imagem com formato=post_unico)
 - Criar CapaReels (via /api/gerar-conteudo + /api/gerar-imagem com formato=capa_reels)
 - Criar Thumbnail (via /api/gerar-conteudo + /api/gerar-imagem com formato=thumbnail_youtube)

Dado que os routers sao CAMADAS OPACAS (so delegam pro service), os testes focam
em:
 - Contrato (status codes, body)
 - Propagacao correta do formato
 - Erros amigaveis (sem keys -> 400)
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from main import app
    return TestClient(app, raise_server_exceptions=False)


FORMATOS_NOVOS = ["post_unico", "capa_reels", "thumbnail_youtube"]


# =============================================================================
# /api/gerar-conteudo — base para criar os 3 artefatos
# =============================================================================
class TestGerarConteudoRouter:
    def test_sem_api_key_retorna_400(self, client, monkeypatch):
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        resp = client.post(
            "/api/gerar-conteudo",
            json={"disciplina": "D1", "tecnologia": "YOLO", "total_slides": 10},
        )
        assert resp.status_code == 400
        assert "API key" in resp.json().get("detail", "")

    def test_infografico_forca_1_slide(self, client, monkeypatch):
        """Qualquer total_slides vira 1 quando tipo_carrossel=infografico.
        Testa a logica interna do router."""
        monkeypatch.setenv("CLAUDE_API_KEY", "fake-key")

        captured = {}
        async def fake_gerar_conteudo(**kwargs):
            captured.update(kwargs)
            return {
                "title": "T",
                "disciplina": "D1",
                "tecnologia_principal": "YOLO",
                "hook_formula": "x",
                "slides": [{"type": "cover", "headline": "H"}],
                "legenda_linkedin": "L",
            }

        with patch("routers.conteudo.gerar_conteudo", new=fake_gerar_conteudo):
            resp = client.post(
                "/api/gerar-conteudo",
                json={
                    "disciplina": "D1",
                    "tecnologia": "YOLO",
                    "total_slides": 10,  # sera forcado pra 1
                    "tipo_carrossel": "infografico",
                },
            )

        # Router deve ter passado total_slides=1 para o service
        assert resp.status_code == 200
        assert captured["total_slides"] == 1


# =============================================================================
# /api/gerar-imagem — Gemini
# =============================================================================
class TestGerarImagemRouter:
    def _body(self, formato):
        return {
            "slides": [{"type": "cover", "headline": "H", "subline": "S"}],
            "formato": formato,
        }

    def test_sem_gemini_key_retorna_400(self, client, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        resp = client.post("/api/gerar-imagem", json=self._body("post_unico"))
        assert resp.status_code == 400
        assert "GEMINI_API_KEY" in resp.json().get("detail", "")

    @pytest.mark.parametrize("formato", FORMATOS_NOVOS)
    def test_propaga_formato_para_service(self, client, monkeypatch, formato):
        monkeypatch.setenv("GEMINI_API_KEY", "fake")

        captured = {}
        async def fake_gerar(*args, **kwargs):
            captured.update(kwargs)
            return ["data:image/png;base64,X"]

        with patch("services.smart_image_service.gerar_imagens_smart", new=fake_gerar), \
             patch("services.brand_prompt_builder.listar_brands", return_value=[{"slug": "itvalley"}]):
            resp = client.post("/api/gerar-imagem", json=self._body(formato))

        assert resp.status_code == 200
        assert captured.get("formato") == formato

    def test_formato_invalido_retorna_422(self, client, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "fake")
        resp = client.post(
            "/api/gerar-imagem",
            json={"slides": [{"type": "cover"}], "formato": "formato_nao_suportado"},
        )
        # Pydantic Literal retorna 422
        assert resp.status_code == 422


# =============================================================================
# /api/gerar-imagem-slide — Gemini single slide
# =============================================================================
class TestGerarImagemSlideRouter:
    def _body(self, formato):
        return {
            "slide": {"type": "cover", "headline": "H"},
            "slide_index": 0,
            "total_slides": 1,
            "formato": formato,
        }

    def test_sem_gemini_key_retorna_400(self, client, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        resp = client.post("/api/gerar-imagem-slide", json=self._body("post_unico"))
        assert resp.status_code == 400

    @pytest.mark.parametrize("formato", FORMATOS_NOVOS)
    def test_aceita_3_formatos(self, client, monkeypatch, formato):
        monkeypatch.setenv("GEMINI_API_KEY", "fake")

        async def fake_gerar(*args, **kwargs):
            return "data:image/png;base64,X"

        with patch("routers.imagem.gerar_imagem_slide", new=fake_gerar):
            resp = client.post("/api/gerar-imagem-slide", json=self._body(formato))

        assert resp.status_code == 200
        assert resp.json() == {"image": "data:image/png;base64,X"}
