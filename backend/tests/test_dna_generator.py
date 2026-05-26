"""Testes unitarios — services/dna_generator.py.

Cobre caso de uso: Regerar DNA Marca com IA (7 dos 17 casos de uso do dominio Marca).

Regras de negocio validadas:
- GEMINI_API_KEY obrigatorio
- Marca precisa existir no disco/mongo
- Marca precisa ter ao menos 1 referencia visual disponivel
- Modo imagem unica: analisa 1 img isolada
- Modo pool separado: analisa com_avatar e sem_avatar independentes
"""

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import anyio
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services import dna_generator


FAKE_DNA = {
    "estilo": "dark_premium",
    "cores": "roxo e preto",
    "tipografia": "outfit bold",
    "elementos": "wireframe holografico",
    "padrao_visual": {"estilo_card": "glass"},
}


class TestRegenerarDnaValidacoes:
    def test_exige_gemini_api_key(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        async def run():
            with pytest.raises(RuntimeError, match="GEMINI_API_KEY nao configurada"):
                await dna_generator.regenerar_dna("itvalley")

        anyio.run(run)

    def test_rejeita_marca_inexistente(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "k")

        async def run():
            with patch("services.dna_generator.carregar_brand", return_value=None):
                with pytest.raises(ValueError, match="nao encontrada"):
                    await dna_generator.regenerar_dna("nope")

        anyio.run(run)


class TestRegenerarDnaImagemUnica:
    def test_modo_imagem_unica_chama_extrair_com_1_img(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "k")
        saved = {}
        captured = {}

        def fake_salvar(slug, brand, overwrite=False):
            saved["brand"] = brand
            return brand

        async def run():
            with patch("services.dna_generator.carregar_brand", return_value={"slug": "x"}):
                with patch("services.dna_generator.salvar_brand", side_effect=fake_salvar):
                    with patch(
                        "skills.dna_extractor.extrair_dna",
                        new=AsyncMock(return_value=dict(FAKE_DNA)),
                    ) as mock_extrair:
                        result = await dna_generator.regenerar_dna("x", imagem_b64="base64")
                        captured["result"] = result
                        captured["mock"] = mock_extrair

        anyio.run(run)
        mock_extrair = captured["mock"]
        result = captured["result"]
        mock_extrair.assert_called_once()
        imagens_passadas = mock_extrair.call_args.args[0]
        assert imagens_passadas == ["base64"]
        assert result["slug"] == "x"
        assert result["refs_analisadas"] == {"unica": 1}
        # padrao_visual separado do dna
        assert "padrao_visual" not in saved["brand"]["dna"]
        assert saved["brand"]["padrao_visual"] == {"estilo_card": "glass"}


class TestRegenerarDnaPoolSeparado:
    def test_sem_refs_em_nenhum_pool_erra(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "k")

        async def run():
            with patch("services.dna_generator.carregar_brand", return_value={"slug": "x"}):
                with patch(
                    "factories.imagem_factory._load_references_by_pool", return_value=[]
                ):
                    with pytest.raises(ValueError, match="nao tem nenhuma referencia"):
                        await dna_generator.regenerar_dna("x")

        anyio.run(run)

    def test_com_refs_em_ambos_pools_analisa_separado(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "k")
        saved = {}
        captured = {}

        def fake_salvar(slug, brand, overwrite=False):
            saved["brand"] = brand
            return brand

        def refs_por_pool(slug, pool):
            if pool == "com_avatar":
                return ["img_ca_1", "img_ca_2"]
            if pool == "sem_avatar":
                return ["img_sa_1"]
            return []

        async def run():
            with patch("services.dna_generator.carregar_brand", return_value={"slug": "x"}):
                with patch("services.dna_generator.salvar_brand", side_effect=fake_salvar):
                    with patch(
                        "factories.imagem_factory._load_references_by_pool",
                        side_effect=refs_por_pool,
                    ):
                        with patch(
                            "skills.dna_extractor.extrair_dna",
                            new=AsyncMock(
                                return_value={
                                    "estilo": "e",
                                    "cores": "c",
                                    "tipografia": "t",
                                    "elementos": "el",
                                    "padrao_visual": {"k": "v"},
                                }
                            ),
                        ) as mock_extrair:
                            result = await dna_generator.regenerar_dna("x")
                            captured["result"] = result
                            captured["mock"] = mock_extrair

        anyio.run(run)
        mock_extrair = captured["mock"]
        result = captured["result"]
        assert mock_extrair.call_count == 2
        assert result["refs_analisadas"] == {"com_avatar": 2, "sem_avatar": 1}
        # padrao_visual guardado por pool
        assert "com_avatar" in saved["brand"]["padrao_visual"]
        assert "sem_avatar" in saved["brand"]["padrao_visual"]

    def test_com_refs_so_em_um_pool_ainda_salva(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "k")
        saved = {}
        captured = {}

        def fake_salvar(slug, brand, overwrite=False):
            saved["brand"] = brand
            return brand

        def refs_por_pool(slug, pool):
            if pool == "com_avatar":
                return ["img1"]
            return []  # sem_avatar vazio

        async def run():
            with patch("services.dna_generator.carregar_brand", return_value={"slug": "x"}):
                with patch("services.dna_generator.salvar_brand", side_effect=fake_salvar):
                    with patch(
                        "factories.imagem_factory._load_references_by_pool",
                        side_effect=refs_por_pool,
                    ):
                        with patch(
                            "skills.dna_extractor.extrair_dna",
                            new=AsyncMock(
                                return_value={
                                    "estilo": "e",
                                    "cores": "c",
                                    "tipografia": "t",
                                    "elementos": "el",
                                    "padrao_visual": {"k": "v"},
                                }
                            ),
                        ):
                            result = await dna_generator.regenerar_dna("x")
                            captured["result"] = result

        anyio.run(run)
        result = captured["result"]
        assert result["refs_analisadas"] == {"com_avatar": 1, "sem_avatar": 0}
        assert "com_avatar" in saved["brand"]["padrao_visual"]
        assert "sem_avatar" not in saved["brand"]["padrao_visual"]
