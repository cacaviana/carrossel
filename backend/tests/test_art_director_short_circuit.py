"""Art Director tem short-circuit quando avatar_mode='sem'.

Motivacao: cada ref da marca ja e template completo (fundo + card + logo + cores).
Descricoes longas do Art Director conflitavam com a composicao da ref visual que
o Gemini recebe. Pra slides sem avatar, pulamos o Claude e geramos descricao
minima que so troca o texto, preservando a composicao da ref.
"""

import asyncio
import pytest

from agents.art_director import executar, _short_circuit_sem_avatar, _todos_slides_viram_sem_avatar


SAMPLE_COPY = {
    "slides": [
        {"titulo": "VibeCoding", "corpo": "um mundo novo"},
        {"titulo": "Segundo slide", "corpo": "texto de apoio"},
    ]
}


class TestShortCircuitDireto:

    def test_retorna_prompt_por_slide(self):
        result = _short_circuit_sem_avatar(SAMPLE_COPY)
        assert "prompts" in result
        assert len(result["prompts"]) == 2

    def test_marca_provider_como_short_circuit(self):
        result = _short_circuit_sem_avatar(SAMPLE_COPY)
        assert result["_provider"] == "short_circuit_sem_avatar"

    def test_cada_slide_tem_campos_esperados(self):
        result = _short_circuit_sem_avatar(SAMPLE_COPY)
        for p in result["prompts"]:
            assert "slide_index" in p
            assert "prompt" in p
            assert "illustration_description" in p
            assert p["pool_usado"] == "sem_avatar"
            assert p["composicao_usada"] == "copiar_da_referencia"

    def test_illustration_inclui_titulo_e_corpo(self):
        result = _short_circuit_sem_avatar(SAMPLE_COPY)
        illu = result["prompts"][0]["illustration_description"]
        assert "VibeCoding" in illu
        assert "um mundo novo" in illu

    def test_illustration_manda_reproduzir_composicao_da_ref(self):
        """Eh a regra central: composicao vem da ref, nao do art director."""
        result = _short_circuit_sem_avatar(SAMPLE_COPY)
        illu = result["prompts"][0]["illustration_description"]
        # Prompt agora em ingles (Gemini 3 Pro interpreta melhor)
        assert "replicate the attached reference" in illu.lower()

    def test_illustration_nao_prescreve_estilo_visual(self):
        """Art director NAO deve descrever fundo/cores/gradiente/ondas — isso vem da ref."""
        result = _short_circuit_sem_avatar(SAMPLE_COPY)
        illu = result["prompts"][0]["illustration_description"].lower()
        # Nao prescreve cores nem estilo
        for termo_proibido in ("gradient fullscreen", "fundo gradiente", "ondas decorativas", "background azul"):
            assert termo_proibido not in illu

    def test_illustration_reforca_preservar_cores(self):
        """Reforco anti-arcoiris: Gemini tende a saturar cores pastel da ref.
        Instrucoes firmes em ingles (Gemini 3 Pro entende melhor):
        - BACKGROUND: pure white stays white, no gradient/tint
        - COLORS: exact RGB, no saturation, no hue shift
        """
        result = _short_circuit_sem_avatar(SAMPLE_COPY)
        illu = result["prompts"][0]["illustration_description"]
        # Background pure white enforcement
        assert "PURE WHITE" in illu
        assert "do NOT add gradients" in illu or "DO NOT add gradients" in illu
        # Color preservation
        assert "EXACT" in illu  # EXACT colors/background
        assert "DO NOT saturate" in illu
        assert "DO NOT shift hue" in illu

    def test_slide_sem_corpo_nao_quebra(self):
        copy = {"slides": [{"titulo": "so titulo"}]}
        result = _short_circuit_sem_avatar(copy)
        assert len(result["prompts"]) == 1
        assert "so titulo" in result["prompts"][0]["illustration_description"]

    def test_copy_vazio_retorna_prompts_vazios(self):
        result = _short_circuit_sem_avatar({"slides": []})
        assert result["prompts"] == []


class TestQuandoDeveShortCircuit:
    """Condicao ampliada: alem de avatar_mode='sem', tambem ativa quando a brand
    nao tem REFS FISICAS no pool com_avatar (consulta direta ao Mongo)."""

    def test_avatar_mode_sem_sempre_short_circuit(self):
        # avatar_mode=sem nao consulta nada — short-circuit imediato
        assert _todos_slides_viram_sem_avatar("sem", None) is True
        assert _todos_slides_viram_sem_avatar("sem", {"slug": "qualquer"}) is True

    def test_brand_palette_none_fluxo_normal(self):
        assert _todos_slides_viram_sem_avatar("livre", None) is False

    def test_brand_sem_slug_fluxo_normal(self):
        assert _todos_slides_viram_sem_avatar("livre", {"nome": "X"}) is False

    def test_brand_com_refs_fisicas_com_avatar_nao_short_circuit(self, monkeypatch):
        """Se Mongo retorna refs no pool com_avatar, fluxo normal (art_director roda)."""
        import agents.art_director as ad
        from factories.imagem_factory import RefDoc

        # Mock _load_ref_docs_by_pool pra retornar refs no com_avatar
        def fake_load(slug, pool):
            if pool == "com_avatar":
                return [RefDoc(b64="xxxx", layout_tag=None)]
            return []

        import factories.imagem_factory as factory_mod
        monkeypatch.setattr(factory_mod, "_load_ref_docs_by_pool", fake_load)

        brand = {"slug": "brand-completa"}
        assert _todos_slides_viram_sem_avatar("livre", brand) is False
        assert _todos_slides_viram_sem_avatar("capa", brand) is False
        assert _todos_slides_viram_sem_avatar("sim", brand) is False

    def test_brand_sem_refs_fisicas_com_avatar_short_circuit(self, monkeypatch):
        """Cenario LinkedIn real: padrao_visual.com_avatar tem texto, mas 0 refs fisicas."""
        import factories.imagem_factory as factory_mod

        def fake_load(slug, pool):
            if pool == "com_avatar":
                return []  # nenhuma ref fisica
            return []

        monkeypatch.setattr(factory_mod, "_load_ref_docs_by_pool", fake_load)

        # Mesmo com padrao_visual.com_avatar populado textualmente, se nao ha ref fisica — short-circuit
        brand = {"slug": "linkedin", "padrao_visual": {"com_avatar": {"tipo_foto": "editorial"}}}
        assert _todos_slides_viram_sem_avatar("livre", brand) is True
        assert _todos_slides_viram_sem_avatar("capa", brand) is True

    def test_mongo_falha_mantem_fluxo_normal(self, monkeypatch):
        """Se Mongo da erro, NAO short-circuit (seguranca — nao pula Art Director por acidente)."""
        import factories.imagem_factory as factory_mod

        def fake_load(slug, pool):
            raise RuntimeError("Mongo down")

        monkeypatch.setattr(factory_mod, "_load_ref_docs_by_pool", fake_load)

        brand = {"slug": "linkedin"}
        assert _todos_slides_viram_sem_avatar("livre", brand) is False


class TestExecutarComSemAvatar:
    """Quando executar decide short-circuit, NAO chama Claude."""

    def test_avatar_mode_sem_usa_short_circuit(self, monkeypatch):
        """Claude NAO deve ser chamado. Se fosse, o mock abaixo falharia."""
        import agents.art_director as ad

        class _Boom:
            def __init__(self, *a, **kw): raise AssertionError("Claude nao deveria ter sido chamado")

        monkeypatch.setattr(ad, "anthropic", type("M", (), {"AsyncAnthropic": _Boom}))

        result = asyncio.run(executar(
            copy=SAMPLE_COPY, hook="",
            formato="post_unico",
            avatar_mode="sem",
            claude_api_key="x",
        ))
        assert result["_provider"] == "short_circuit_sem_avatar"
        assert len(result["prompts"]) == 2

    def test_avatar_mode_livre_com_brand_so_sem_avatar_usa_short_circuit(self, monkeypatch):
        """Caso LinkedIn real: avatar_mode='livre' mas brand sem refs com_avatar."""
        import agents.art_director as ad

        class _Boom:
            def __init__(self, *a, **kw): raise AssertionError("Claude nao deveria ter sido chamado")

        monkeypatch.setattr(ad, "anthropic", type("M", (), {"AsyncAnthropic": _Boom}))

        brand = {"slug": "linkedin", "padrao_visual": {"com_avatar": {}, "sem_avatar": {"tipo_foto": "editorial"}}}
        result = asyncio.run(executar(
            copy=SAMPLE_COPY, hook="",
            formato="post_unico",
            avatar_mode="livre",
            brand_palette=brand,
            claude_api_key="x",
        ))
        assert result["_provider"] == "short_circuit_sem_avatar"

    def test_avatar_mode_livre_com_brand_completa_chama_claude(self, monkeypatch):
        """Brand com refs FISICAS no com_avatar: fluxo normal, Claude eh chamado."""
        import agents.art_director as ad
        import factories.imagem_factory as factory_mod
        from factories.imagem_factory import RefDoc

        # Mock: brand "outra" TEM refs fisicas no com_avatar
        def fake_load(slug, pool):
            if pool == "com_avatar":
                return [RefDoc(b64="xxx", layout_tag=None)]
            return []
        monkeypatch.setattr(factory_mod, "_load_ref_docs_by_pool", fake_load)

        class _FakeMsg:
            def __init__(self, text): self.content = [type("X", (), {"text": text})]

        class _FakeMessages:
            async def create(self, **kw):
                return _FakeMsg('{"prompts":[{"slide_index":1,"prompt":"t","illustration_description":"desc"}]}')

        class _FakeClient:
            def __init__(self, api_key): self.messages = _FakeMessages()

        monkeypatch.setattr(ad, "anthropic", type("M", (), {"AsyncAnthropic": _FakeClient}))

        brand = {"slug": "outra", "padrao_visual": {"com_avatar": {"tipo_foto": "editorial"}, "sem_avatar": {}}}
        result = asyncio.run(executar(
            copy=SAMPLE_COPY, hook="",
            formato="post_unico",
            avatar_mode="livre",
            brand_palette=brand,
            claude_api_key="x",
        ))
        assert result["_provider"] != "short_circuit_sem_avatar"
