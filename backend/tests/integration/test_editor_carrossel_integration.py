"""Integracao Editar Carrossel.

Caso de uso: Editor manual pos-geracao.
Rotas cobertas:
- POST /api/editor/salvar-pdf        (gera PDF a partir de slides editados + logo)
- GET  /api/editor/slides/{brand}    (retorna slides limpos pra re-edicao)
- POST /api/editor/corrigir-texto    (corrige texto OU aplica instrucao custom)
- POST /api/editor/ajustar-imagem    (ajuste image-to-image via Gemini)

Criterios de aceite (ClickUp 86e0y9djc):
- Editor livre por slide
- Logo posicionavel manualmente
- Texto editavel inline (via corrigir-texto ou instrucao)
- Salvar versao editada (via salvar-pdf)
"""

import base64
import io
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image


def _png_base64(w=60, h=60, color=(30, 30, 30)) -> str:
    """Gera PNG pequeno em memoria e devolve como data URL base64."""
    img = Image.new("RGB", (w, h), color=color)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


@pytest.fixture
def sample_slides():
    """Payload minimo valido de 2 slides."""
    return [
        {"image": _png_base64(), "logo_x": 540, "logo_y": 1290, "logo_size": 80},
        {"image": _png_base64(color=(80, 80, 80)), "logo_x": 540, "logo_y": 1290, "logo_size": 80},
    ]


class TestEditorSalvarPdf:
    """POST /api/editor/salvar-pdf — gerar PDF final com logo posicionado."""

    def test_sem_body_retorna_400(self, client, admin_headers):
        resp = client.post("/api/editor/salvar-pdf", headers=admin_headers, json={})
        assert resp.status_code == 400

    def test_sem_slides_retorna_400(self, client, admin_headers):
        resp = client.post(
            "/api/editor/salvar-pdf",
            headers=admin_headers,
            json={"slides": [], "logo": _png_base64(20, 20)},
        )
        assert resp.status_code == 400

    def test_sem_logo_retorna_400(self, client, admin_headers, sample_slides):
        resp = client.post(
            "/api/editor/salvar-pdf",
            headers=admin_headers,
            json={"slides": sample_slides, "logo": ""},
        )
        assert resp.status_code == 400

    def test_slides_e_logo_validos_retorna_pdf_base64(self, client, admin_headers, sample_slides):
        logo = _png_base64(40, 40, color=(200, 50, 50))
        resp = client.post(
            "/api/editor/salvar-pdf",
            headers=admin_headers,
            json={"slides": sample_slides, "logo": logo, "formato": "carrossel"},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "pdf_base64" in body
        assert "total_slides" in body
        assert body["total_slides"] == 2
        # Valida que o base64 decodifica pra um PDF (header %PDF-)
        decoded = base64.b64decode(body["pdf_base64"])
        assert decoded[:5] == b"%PDF-"

    def test_logo_desligado_nao_quebra(self, client, admin_headers, sample_slides):
        """logo_size=0 em todos os slides significa 'sem logo' — deve gerar PDF sem crash."""
        for s in sample_slides:
            s["logo_size"] = 0
        resp = client.post(
            "/api/editor/salvar-pdf",
            headers=admin_headers,
            json={"slides": sample_slides, "logo": _png_base64(20, 20)},
        )
        assert resp.status_code == 200

    def test_formato_reels_gera_pdf(self, client, admin_headers, sample_slides):
        resp = client.post(
            "/api/editor/salvar-pdf",
            headers=admin_headers,
            json={"slides": sample_slides[:1], "logo": _png_base64(20, 20), "formato": "capa_reels"},
        )
        assert resp.status_code == 200
        assert resp.json()["total_slides"] == 1

    @pytest.mark.parametrize("formato", ["carrossel", "post_unico", "capa_reels", "thumbnail_youtube"])
    def test_salvar_pdf_funciona_para_cada_formato(self, client, admin_headers, sample_slides, formato):
        """Editor pos-geracao reaproveitado para os 4 formatos (PostUnico Editar, Reels Editar, Thumbnail Editar)."""
        resp = client.post(
            "/api/editor/salvar-pdf",
            headers=admin_headers,
            json={"slides": sample_slides[:1], "logo": _png_base64(20, 20), "formato": formato},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["total_slides"] == 1


class TestEditorSlidesLimpos:
    """GET /api/editor/slides/{brand} — serve JSON de slides limpos."""

    def test_brand_inexistente_retorna_404(self, client, admin_headers):
        resp = client.get("/api/editor/slides/marca-que-nao-existe-xyz", headers=admin_headers)
        assert resp.status_code == 404

    def test_brand_existente_retorna_json(self, client, admin_headers, tmp_path, monkeypatch):
        """Mocka buscar_slides_limpos pra nao depender de arquivo em disco."""
        import services.editor_service as es

        fake_payload = {"brand": "itvalley", "slides": [{"index": 1, "image": "data:..."}]}

        def fake_buscar(brand: str):
            return fake_payload if brand == "itvalley" else None

        monkeypatch.setattr(es, "buscar_slides_limpos", fake_buscar, raising=True)
        # config.py importa via `buscar_slides_limpos as _buscar_slides_limpos` — precisa override la tb
        import routers.config as cfg
        monkeypatch.setattr(cfg, "_buscar_slides_limpos", fake_buscar, raising=True)

        resp = client.get("/api/editor/slides/itvalley", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json() == fake_payload


class TestEditorCorrigirTexto:
    """POST /api/editor/corrigir-texto — corrige texto ou aplica instrucao."""

    def test_com_instrucao_custom_chama_aplicar_instrucao(self, client, admin_headers, monkeypatch):
        """Se 'instrucao' vem no body, chama aplicar_instrucao (image-to-image com prompt livre)."""
        import services.editor_service as es

        called = {}

        async def fake_aplicar(image, instrucao):
            called["image"] = image
            called["instrucao"] = instrucao
            return {"image": _png_base64(), "tentativas": 1}

        monkeypatch.setattr(es, "aplicar_instrucao", fake_aplicar, raising=True)

        resp = client.post(
            "/api/editor/corrigir-texto",
            headers=admin_headers,
            json={"image": _png_base64(), "instrucao": "remover texto"},
        )
        assert resp.status_code == 200, resp.text
        assert "image" in resp.json()
        assert called["instrucao"] == "remover texto"

    def test_sem_instrucao_chama_corrigir_texto(self, client, admin_headers, monkeypatch):
        """Sem instrucao, chama corrigir_texto (OCR + fix)."""
        import services.editor_service as es
        import routers.config as cfg

        async def fake_corrigir(image, slide):
            return {
                "image": _png_base64(),
                "tentativas": 1,
                "texto_lido": "OK",
            }

        monkeypatch.setattr(es, "corrigir_texto", fake_corrigir, raising=True)
        monkeypatch.setattr(cfg, "_corrigir_texto", fake_corrigir, raising=True)

        resp = client.post(
            "/api/editor/corrigir-texto",
            headers=admin_headers,
            json={"image": _png_base64(), "slide": {"titulo": "Oi", "corpo": "mundo"}},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "image" in body
        assert body["tentativas"] == 1

    def test_falha_na_correcao_retorna_500(self, client, admin_headers, monkeypatch):
        import services.editor_service as es
        import routers.config as cfg

        async def fake_corrigir(image, slide):
            return None

        monkeypatch.setattr(es, "corrigir_texto", fake_corrigir, raising=True)
        monkeypatch.setattr(cfg, "_corrigir_texto", fake_corrigir, raising=True)

        resp = client.post(
            "/api/editor/corrigir-texto",
            headers=admin_headers,
            json={"image": _png_base64(), "slide": {}},
        )
        assert resp.status_code == 500


class TestEditorAjustarImagem:
    """POST /api/editor/ajustar-imagem — ajuste image-to-image."""

    def test_sem_gemini_key_retorna_400(self, client, admin_headers, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        resp = client.post(
            "/api/editor/ajustar-imagem",
            headers=admin_headers,
            json={"imagem": _png_base64(), "feedback": "mais contraste"},
        )
        assert resp.status_code == 400

    def test_sem_imagem_retorna_400(self, client, admin_headers, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
        resp = client.post(
            "/api/editor/ajustar-imagem",
            headers=admin_headers,
            json={"imagem": "", "feedback": "x"},
        )
        assert resp.status_code == 400

    def test_sem_feedback_retorna_400(self, client, admin_headers, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
        resp = client.post(
            "/api/editor/ajustar-imagem",
            headers=admin_headers,
            json={"imagem": _png_base64(), "feedback": ""},
        )
        assert resp.status_code == 400

    def test_ajuste_com_mock_retorna_imagem(self, client, admin_headers, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

        async def fake_ajustar(clientx, imagem, feedback, api_key, ref_image_b64=None):
            return {"image": _png_base64(), "feedback_aplicado": feedback}

        import utils.image_adjuster as adj
        monkeypatch.setattr(adj, "ajustar_imagem", fake_ajustar, raising=True)

        resp = client.post(
            "/api/editor/ajustar-imagem",
            headers=admin_headers,
            json={"imagem": _png_base64(), "feedback": "mais saturacao"},
        )
        assert resp.status_code == 200, resp.text
        assert "image" in resp.json()


class TestContratoEditor:
    """Rotas registradas no OpenAPI."""

    def test_rotas_expostas(self, client):
        resp = client.get("/openapi.json")
        paths = resp.json()["paths"]
        esperadas = [
            ("/api/editor/salvar-pdf", "post"),
            ("/api/editor/slides/{brand}", "get"),
            ("/api/editor/corrigir-texto", "post"),
            ("/api/editor/ajustar-imagem", "post"),
        ]
        for path, method in esperadas:
            assert path in paths, f"Rota nao registrada: {path}"
            assert method in paths[path], f"Metodo {method} ausente em {path}"
