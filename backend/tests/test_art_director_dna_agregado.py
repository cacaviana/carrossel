"""Art director injeta dna_agregado da brand no prompt do Claude.

Substitui o DNA antigo (que podia estar sujo, ex: 'astronauta OVNI') pelo
agregado real extraido das refs.
"""

import asyncio
import json

import pytest

from agents.art_director import _carregar_dna_agregado, executar


SAMPLE_COPY = {"slides": [{"titulo": "Vibecoding", "corpo": "novo jeito"}]}

DNA_FAKE = {
    "constantes": {
        "paleta": ["#FFFFFF"],
        "tipografia": "texto branco grande bold",
        "tom_cores": "alto_contraste",
        "elementos_recorrentes": ["homem", "logo"],
        "estilo_geral": "thumb impactante com pessoa em destaque",
    },
    "variaveis_livres": {
        "fundo": ["auditorio escuro", "cenario digital"],
        "composicao": ["pessoa direita texto esquerda"],
        "outros": [],
    },
    "n_refs_analisadas": 6,
}


class TestCarregarDnaAgregado:

    def test_brand_palette_com_dna_agregado_inline(self):
        bp = {"slug": "x", "dna_agregado": DNA_FAKE}
        assert _carregar_dna_agregado(bp) == DNA_FAKE

    def test_sem_brand_palette(self):
        assert _carregar_dna_agregado(None) is None

    def test_sem_slug(self):
        assert _carregar_dna_agregado({"nome": "x"}) is None

    def test_busca_no_mongo_se_nao_inline(self, monkeypatch):
        """Se brand_palette nao tem dna_agregado, busca no Mongo via slug."""
        from unittest.mock import MagicMock
        fake_db = MagicMock()
        fake_db.brands.find_one.return_value = {"dna_agregado": DNA_FAKE}

        import data.connections.mongo_connection as conn
        monkeypatch.setattr(conn, "get_mongo_db", lambda: fake_db)

        result = _carregar_dna_agregado({"slug": "thumbs"})
        assert result == DNA_FAKE
        fake_db.brands.find_one.assert_called_once()


class TestPromptIncluiDnaAgregado:
    """Quando art_director chama Claude/OpenAI, o prompt deve incluir o DNA agregado."""

    def test_prompt_contem_constantes_e_variaveis(self, monkeypatch):
        import agents.art_director as ad

        # Mock loader pra retornar DNA fake
        monkeypatch.setattr(ad, "_carregar_dna_agregado", lambda bp: DNA_FAKE)

        # Mock _todos_slides_viram_sem_avatar pra forçar fluxo normal (nao short_circuit)
        monkeypatch.setattr(ad, "_todos_slides_viram_sem_avatar", lambda *a, **kw: False)

        # Captura o prompt enviado pro Claude
        captured = {}

        class _FakeMsg:
            def __init__(self, t): self.content = [type("X", (), {"text": t})]

        class _FakeMessages:
            async def create(self, **kw):
                captured["user_prompt"] = kw["messages"][0]["content"]
                return _FakeMsg('{"prompts":[{"slide_index":1,"prompt":"x","illustration_description":"y"}]}')

        class _FakeClient:
            def __init__(self, api_key): self.messages = _FakeMessages()

        monkeypatch.setattr(ad, "anthropic", type("M", (), {"AsyncAnthropic": _FakeClient}))

        asyncio.run(executar(
            copy=SAMPLE_COPY, hook="", formato="thumbnail_youtube",
            brand_palette={"slug": "thumbs"},
            avatar_mode="sim",
            claude_api_key="k",
        ))

        prompt = captured["user_prompt"]
        # Inclui as constantes
        assert "DNA AGREGADO" in prompt
        assert "#FFFFFF" in prompt
        assert "homem, logo" in prompt
        assert "thumb impactante" in prompt
        # Inclui variaveis
        assert "auditorio escuro" in prompt
        # Aviso anti-alucinacao
        assert "nao adicionar astronauta" in prompt.lower()

    def test_sem_dna_agregado_nao_quebra(self, monkeypatch):
        """Se brand nao tem dna_agregado, fluxo segue normal (sem o bloco)."""
        import agents.art_director as ad

        monkeypatch.setattr(ad, "_carregar_dna_agregado", lambda bp: None)
        monkeypatch.setattr(ad, "_todos_slides_viram_sem_avatar", lambda *a, **kw: False)

        captured = {}

        class _FakeMsg:
            def __init__(self, t): self.content = [type("X", (), {"text": t})]

        class _FakeMessages:
            async def create(self, **kw):
                captured["user_prompt"] = kw["messages"][0]["content"]
                return _FakeMsg('{"prompts":[{"slide_index":1,"prompt":"x","illustration_description":"y"}]}')

        class _FakeClient:
            def __init__(self, api_key): self.messages = _FakeMessages()

        monkeypatch.setattr(ad, "anthropic", type("M", (), {"AsyncAnthropic": _FakeClient}))

        asyncio.run(executar(
            copy=SAMPLE_COPY, hook="", formato="thumbnail_youtube",
            brand_palette={"slug": "x"},
            avatar_mode="sim",
            claude_api_key="k",
        ))

        prompt = captured["user_prompt"]
        # Nao tem o bloco DNA AGREGADO
        assert "DNA AGREGADO" not in prompt
