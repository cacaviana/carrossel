"""Testes unitarios — BrandAnalyzerService (camada opaca).

Cobre services/brand_analyzer_service.py — orquestra o BrandAnalyzer (factory).
Caso de uso: Analisar Padrao Visual Pool.

Filosofia IT Valley: Service eh camada opaca — so chama Factory e Mapper.
Nao conhece campos do DTO. Aqui validamos:
- api key obrigatoria (GEMINI_API_KEY)
- envia os parametros certos pro factory
- wrappea o resultado em AnalisarReferenciasResponse
"""

import os
import sys
from unittest.mock import AsyncMock, patch

import anyio
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.brand_analyzer_service import BrandAnalyzerService
from dtos.brand.analisar_referencias.response import AnalisarReferenciasResponse


FAKE_GEMINI_RESPONSE = {
    "cores": {
        "fundo": "#0A0A0F",
        "gradiente_de": "#1A1A2E",
        "gradiente_ate": "#16213E",
        "card": "#1E1E2E",
        "card_borda": "rgba(0,0,0,0.2)",
        "acento_principal": "#A78BFA",
        "acento_secundario": "#6D28D9",
        "texto_principal": "#FFFFFF",
        "texto_secundario": "#94A3B8",
        "acento_negativo": "#F87171",
    },
    "visual": {
        "estilo_fundo": "gradient",
        "estilo_elemento": {"tipo": "wireframe"},
        "estilo_card": "glass",
        "estilo_texto": "bold",
        "estilo_desenho": "line-art",
        "regras_extras": "nada neon",
    },
    "atmosfera": "premium dark",
    "sugestao_nome": "IT Valley",
}


class TestAnalisar:
    def test_exige_gemini_api_key(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        async def run():
            with pytest.raises(ValueError, match="GEMINI_API_KEY nao configurada"):
                await BrandAnalyzerService.analisar(["b64"], "marca", "desc")

        anyio.run(run)

    def test_chama_factory_e_retorna_response_pydantic(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
        captured = {}

        async def run():
            with patch(
                "services.brand_analyzer_service.BrandAnalyzer.analisar",
                new=AsyncMock(return_value=FAKE_GEMINI_RESPONSE),
            ) as mock_factory:
                resp = await BrandAnalyzerService.analisar(
                    ["b64img"], "IT Valley", "Escola de IA"
                )
                captured["resp"] = resp
                captured["mock"] = mock_factory

        anyio.run(run)
        resp = captured["resp"]
        mock_factory = captured["mock"]
        assert isinstance(resp, AnalisarReferenciasResponse)
        assert resp.sugestao_nome == "IT Valley"
        mock_factory.assert_called_once()
        call_kwargs = mock_factory.call_args.kwargs
        assert call_kwargs["imagens_b64"] == ["b64img"]
        assert call_kwargs["nome_marca"] == "IT Valley"
        assert call_kwargs["descricao"] == "Escola de IA"
        assert call_kwargs["api_key"] == "fake-key"

    def test_propaga_erro_do_factory(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "k")

        async def run():
            with patch(
                "services.brand_analyzer_service.BrandAnalyzer.analisar",
                new=AsyncMock(side_effect=ValueError("imagem invalida")),
            ):
                with pytest.raises(ValueError, match="imagem invalida"):
                    await BrandAnalyzerService.analisar([], "", "")

        anyio.run(run)


class TestDescreverEstilo:
    def test_exige_gemini_api_key(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        async def run():
            with pytest.raises(ValueError, match="GEMINI_API_KEY nao configurada"):
                await BrandAnalyzerService.descrever_estilo("b64img")

        anyio.run(run)

    def test_delega_para_skill_visual_extractor(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "k")
        captured = {}

        async def run():
            with patch("skills.visual_extractor.extrair", new=AsyncMock(return_value={"estilo": "x"})) as mock_skill:
                result = await BrandAnalyzerService.descrever_estilo("b64img")
                captured["result"] = result
                captured["mock"] = mock_skill

        anyio.run(run)
        assert captured["result"] == {"estilo": "x"}
        captured["mock"].assert_called_once_with("b64img", "k")
