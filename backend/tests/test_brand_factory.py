"""Testes unitarios — Factories do dominio Brand (Marca).

Cobre:
- BrandAnalyzer (factories/brand_analyzer.py) — Gemini Vision, validacao de entrada
- VisualPreferenceFactory (factories/visual_preference_factory.py) — criacao do Model

Filosofia IT Valley: Factory contem regras de negocio (validacoes/invariantes),
nao faz I/O. Quando o factory depende de httpx externo, usamos mocks.

Obs: projeto usa anyio (nao pytest-asyncio), entao rodamos corrotinas via anyio.run.
"""

import os
import sys
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import anyio
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from factories.brand_analyzer import BrandAnalyzer
from factories.visual_preference_factory import VisualPreferenceFactory
from dtos.visual_preference.salvar_preferencia.request import SalvarPreferenciaRequest


def _make_mock_client(fake_json_text: str):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": fake_json_text}]}}]
    }
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=mock_response)
    return mock_client


# ===================================================================
# BrandAnalyzer.analisar — regra de negocio: ao menos 1 imagem
# ===================================================================
class TestBrandAnalyzerValidacao:
    def test_rejeita_lista_vazia_de_imagens(self):
        """RN: Envie ao menos 1 imagem de referencia."""
        async def run():
            with pytest.raises(ValueError, match="ao menos 1 imagem"):
                await BrandAnalyzer.analisar([], "IT Valley", "", "fake-key")
        anyio.run(run)


# ===================================================================
# BrandAnalyzer.analisar — chamada real (mockada) ao Gemini
# ===================================================================
class TestBrandAnalyzerChamada:
    def test_chama_gemini_com_api_key_header(self):
        """Factory envia imagens b64 (max 5) e recebe JSON do Gemini."""
        fake_json_text = (
            '{"cores":{"fundo":"#0A0A0F","gradiente_de":"#1A1A2E",'
            '"gradiente_ate":"#16213E","card":"#1E1E2E",'
            '"card_borda":"rgba(0,0,0,0.2)","acento_principal":"#A78BFA",'
            '"acento_secundario":"#6D28D9","acento_negativo":"#F87171",'
            '"texto_principal":"#FFFFFF","texto_secundario":"#94A3B8"},'
            '"visual":{"estilo_fundo":"x","estilo_elemento":{"tipo":"wireframe"},'
            '"estilo_card":"x","estilo_texto":"x","estilo_desenho":"x","regras_extras":"x"},'
            '"atmosfera":"premium","sugestao_nome":"IT"}'
        )
        mock_client = _make_mock_client(fake_json_text)

        async def run():
            with patch("factories.brand_analyzer.httpx.AsyncClient", return_value=mock_client):
                return await BrandAnalyzer.analisar(["b64img"], "IT Valley", "Escola", "fake-key")

        result = anyio.run(run)
        assert result["atmosfera"] == "premium"
        mock_client.post.assert_called_once()
        kwargs = mock_client.post.call_args.kwargs
        assert kwargs["headers"]["x-goog-api-key"] == "fake-key"

    def test_limita_a_5_imagens(self):
        """Mesmo recebendo 7, factory so deve enviar 5 ao Gemini."""
        fake_json_text = (
            '{"cores":{"fundo":"#000","gradiente_de":"#111","gradiente_ate":"#222",'
            '"card":"#333","card_borda":"rgba(0,0,0,0.1)","acento_principal":"#A78BFA",'
            '"acento_secundario":"#6D28D9","texto_principal":"#FFF","texto_secundario":"#CCC",'
            '"acento_negativo":"#F87171"},'
            '"visual":{"estilo_fundo":"x","estilo_elemento":{},"estilo_card":"x",'
            '"estilo_texto":"x","estilo_desenho":"x","regras_extras":"x"},'
            '"atmosfera":"a","sugestao_nome":"s"}'
        )
        mock_client = _make_mock_client(fake_json_text)
        imgs = [f"b64_{i}" for i in range(7)]

        async def run():
            with patch("factories.brand_analyzer.httpx.AsyncClient", return_value=mock_client):
                await BrandAnalyzer.analisar(imgs, "", "", "key")

        anyio.run(run)
        payload = mock_client.post.call_args.kwargs["json"]
        parts = payload["contents"][0]["parts"]
        # Deve ter 5 imgs + 1 texto = 6 parts
        assert len(parts) == 6
        inline_parts = [p for p in parts if "inline_data" in p]
        assert len(inline_parts) == 5

    def test_strip_data_uri_prefix_antes_de_enviar(self):
        """Se vier data:image/png;base64,XYZ, envia so XYZ pra Gemini."""
        fake_json_text = (
            '{"cores":{"fundo":"#000","gradiente_de":"#111","gradiente_ate":"#222",'
            '"card":"#333","card_borda":"rgba(0,0,0,0.1)","acento_principal":"#A",'
            '"acento_secundario":"#B","texto_principal":"#FFF","texto_secundario":"#CCC",'
            '"acento_negativo":"#F87171"},'
            '"visual":{"estilo_fundo":"x","estilo_elemento":{},"estilo_card":"x",'
            '"estilo_texto":"x","estilo_desenho":"x","regras_extras":"x"},'
            '"atmosfera":"a","sugestao_nome":"s"}'
        )
        mock_client = _make_mock_client(fake_json_text)

        async def run():
            with patch("factories.brand_analyzer.httpx.AsyncClient", return_value=mock_client):
                await BrandAnalyzer.analisar(
                    ["data:image/png;base64,PUREB64"], "", "", "key"
                )

        anyio.run(run)
        payload = mock_client.post.call_args.kwargs["json"]
        inline = payload["contents"][0]["parts"][0]["inline_data"]
        assert inline["data"] == "PUREB64"

    def test_remove_markdown_code_fences_do_json(self):
        """Gemini as vezes retorna ```json ... ``` — factory deve limpar."""
        text_com_fences = (
            '```json\n'
            '{"cores":{"fundo":"#000","gradiente_de":"#111","gradiente_ate":"#222",'
            '"card":"#333","card_borda":"rgba(0,0,0,0.1)","acento_principal":"#A",'
            '"acento_secundario":"#B","texto_principal":"#FFF","texto_secundario":"#CCC",'
            '"acento_negativo":"#F87171"},'
            '"visual":{"estilo_fundo":"x","estilo_elemento":{},"estilo_card":"x",'
            '"estilo_texto":"x","estilo_desenho":"x","regras_extras":"x"},'
            '"atmosfera":"a","sugestao_nome":"s"}\n'
            '```'
        )
        mock_client = _make_mock_client(text_com_fences)

        async def run():
            with patch("factories.brand_analyzer.httpx.AsyncClient", return_value=mock_client):
                return await BrandAnalyzer.analisar(["b64"], "", "", "key")

        result = anyio.run(run)
        assert result["atmosfera"] == "a"


# ===================================================================
# VisualPreferenceFactory — cria Model com tenant_id (RN IT Valley)
# ===================================================================
class TestVisualPreferenceFactory:
    def test_cria_model_com_tenant_id(self):
        dto = SalvarPreferenciaRequest(estilo="dark_premium", aprovado=True)
        model = VisualPreferenceFactory.to_model(dto, tenant_id="t1")
        assert model.tenant_id == "t1"
        assert model.estilo == "dark_premium"
        assert model.aprovado is True
        assert model.contexto is None
        assert isinstance(model.id, uuid.UUID)

    def test_strip_estilo(self):
        dto = SalvarPreferenciaRequest(estilo="  dark_premium  ", aprovado=True)
        model = VisualPreferenceFactory.to_model(dto, tenant_id="t1")
        assert model.estilo == "dark_premium"

    def test_serializa_contexto_como_json(self):
        dto = SalvarPreferenciaRequest(
            estilo="flat",
            aprovado=False,
            contexto={"motivo": "neon demais"},
        )
        model = VisualPreferenceFactory.to_model(dto, tenant_id="t1")
        # contexto eh serializado como JSON string
        assert '"motivo"' in model.contexto
        assert "neon demais" in model.contexto

    def test_contexto_none_quando_nao_passado(self):
        dto = SalvarPreferenciaRequest(estilo="x", aprovado=True, contexto=None)
        model = VisualPreferenceFactory.to_model(dto, tenant_id="t1")
        assert model.contexto is None

    def test_rejeita_estilo_vazio(self):
        dto = SalvarPreferenciaRequest(estilo="   ", aprovado=True)
        with pytest.raises(ValueError, match="Estilo obrigatorio"):
            VisualPreferenceFactory.to_model(dto, tenant_id="t1")

    def test_created_at_preenchido_automaticamente(self):
        dto = SalvarPreferenciaRequest(estilo="dark", aprovado=True)
        model = VisualPreferenceFactory.to_model(dto, tenant_id="t1")
        assert model.created_at is not None

    def test_ids_diferentes_a_cada_chamada(self):
        dto = SalvarPreferenciaRequest(estilo="dark", aprovado=True)
        m1 = VisualPreferenceFactory.to_model(dto, "t1")
        m2 = VisualPreferenceFactory.to_model(dto, "t1")
        assert m1.id != m2.id
