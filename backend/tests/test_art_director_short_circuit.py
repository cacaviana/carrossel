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


def _run(coro):
    """Helper: roda coroutine sincronamente no teste."""
    return asyncio.run(coro)


class TestShortCircuitDireto:
    """Chamadas SEM brand_palette+pipeline_id caem no fallback generico (sem analise)."""

    def test_retorna_prompt_por_slide(self):
        result = _run(_short_circuit_sem_avatar(SAMPLE_COPY))
        assert "prompts" in result
        assert len(result["prompts"]) == 2

    def test_marca_provider_como_short_circuit(self):
        result = _run(_short_circuit_sem_avatar(SAMPLE_COPY))
        assert result["_provider"] == "short_circuit_sem_avatar"

    def test_cada_slide_tem_campos_esperados(self):
        result = _run(_short_circuit_sem_avatar(SAMPLE_COPY))
        for p in result["prompts"]:
            assert "slide_index" in p
            assert "prompt" in p
            assert "illustration_description" in p
            assert p["pool_usado"] == "sem_avatar"
            assert p["composicao_usada"] == "copiar_da_referencia"

    def test_illustration_inclui_titulo_e_corpo(self):
        result = _run(_short_circuit_sem_avatar(SAMPLE_COPY))
        illu = result["prompts"][0]["illustration_description"]
        assert "VibeCoding" in illu
        assert "um mundo novo" in illu

    def test_illustration_manda_reproduzir_composicao_da_ref(self):
        """Fallback sem analise: usa texto em ingles generico."""
        result = _run(_short_circuit_sem_avatar(SAMPLE_COPY))
        illu = result["prompts"][0]["illustration_description"]
        assert "replicate the attached reference" in illu.lower()

    def test_illustration_nao_prescreve_estilo_visual(self):
        """Fallback nao descreve fundo/cores/gradiente — isso vem da ref."""
        result = _run(_short_circuit_sem_avatar(SAMPLE_COPY))
        illu = result["prompts"][0]["illustration_description"].lower()
        for termo_proibido in ("gradient fullscreen", "fundo gradiente", "ondas decorativas", "background azul"):
            assert termo_proibido not in illu

    def test_illustration_reforca_preservar_cores(self):
        """Fallback: PURE WHITE + DO NOT saturate/shift hue."""
        result = _run(_short_circuit_sem_avatar(SAMPLE_COPY))
        illu = result["prompts"][0]["illustration_description"]
        assert "PURE WHITE" in illu
        assert "EXACT" in illu
        assert "DO NOT saturate" in illu
        assert "DO NOT shift hue" in illu

    def test_slide_sem_corpo_nao_quebra(self):
        copy = {"slides": [{"titulo": "so titulo"}]}
        result = _run(_short_circuit_sem_avatar(copy))
        assert len(result["prompts"]) == 1
        assert "so titulo" in result["prompts"][0]["illustration_description"]

    def test_copy_vazio_retorna_prompts_vazios(self):
        result = _run(_short_circuit_sem_avatar({"slides": []}))
        assert result["prompts"] == []


class TestShortCircuitComAnalise:
    """Quando pipeline_id + brand_palette.slug estao presentes, usa analise_visual do Mongo.
    Descricao adapta ao copy (blocos_conteudo)."""

    def test_usa_analise_visual_pra_gerar_prompt(self, monkeypatch):
        """Se o ref_analyzer retorna analise, o prompt gerado usa a paleta + composicao."""
        import agents.art_director as ad

        fake_analise = {
            "composicao": "Fundo branco puro, badge outline topo-esquerdo, 3 caixas empilhadas.",
            "paleta": {
                "fundo": "#FFFFFF",
                "caixa_1": "#E8E2F5",
                "caixa_2": "#E6ECF5",
                "caixa_3": "#E5F2EB",
                "texto_principal": "#0A0A0A",
            },
            "blocos_conteudo": 3,
            "tipo_estrutural": "slide_bullets",
            "tom_cores": "neutro_pastel",
        }

        async def fake_obter_analise(brand_palette, pipeline_id, key):
            return fake_analise

        monkeypatch.setattr(ad, "_obter_analise_ref", fake_obter_analise)

        result = _run(_short_circuit_sem_avatar(
            SAMPLE_COPY,
            brand_palette={"slug": "linkedin"},
            pipeline_id="p-x",
            claude_api_key="k",
        ))
        illu = result["prompts"][0]["illustration_description"]
        # Tem composicao da analise
        assert "badge outline topo-esquerdo" in illu
        # Tem paleta com HEX
        assert "#FFFFFF" in illu
        assert "#E8E2F5" in illu
        # Tem tom cromatico
        assert "neutro_pastel" in illu
        # Nao saturar/mudar matiz
        assert "NAO transforme em cores vivas" in illu

    def test_adapta_blocos_quando_copy_tem_menos_que_ref(self, monkeypatch):
        """Ref tem 3 blocos mas copy tem 1 (so titulo) — deve mandar usar 1 bloco so."""
        import agents.art_director as ad

        fake_analise = {
            "composicao": "3 caixas",
            "paleta": {"fundo": "#FFFFFF"},
            "blocos_conteudo": 3,
            "tom_cores": "neutro_pastel",
        }

        async def fake_obter_analise(*a, **kw):
            return fake_analise

        monkeypatch.setattr(ad, "_obter_analise_ref", fake_obter_analise)

        copy_so_titulo = {"slides": [{"titulo": "Vibecoding"}]}
        result = _run(_short_circuit_sem_avatar(
            copy_so_titulo,
            brand_palette={"slug": "linkedin"},
            pipeline_id="p-x",
            claude_api_key="k",
        ))
        illu = result["prompts"][0]["illustration_description"]
        assert "ADAPTACAO DE BLOCOS" in illu
        assert "APENAS 1 bloco" in illu
        assert "NAO adicione caixas vazias" in illu

    def test_adapta_blocos_quando_copy_tem_mais_que_ref(self, monkeypatch):
        """Ref tem 1 bloco mas copy tem titulo+corpo (2 blocos) — expande a estrutura."""
        import agents.art_director as ad

        fake_analise = {
            "composicao": "capa impacto",
            "paleta": {"fundo": "#FFFFFF"},
            "blocos_conteudo": 1,
            "tom_cores": "vibrante",
        }

        async def fake_obter_analise(*a, **kw):
            return fake_analise

        monkeypatch.setattr(ad, "_obter_analise_ref", fake_obter_analise)

        result = _run(_short_circuit_sem_avatar(
            SAMPLE_COPY,  # 2 slides, cada um com titulo+corpo
            brand_palette={"slug": "linkedin"},
            pipeline_id="p-x",
            claude_api_key="k",
        ))
        illu = result["prompts"][0]["illustration_description"]
        assert "Expanda a estrutura" in illu

    def test_sem_pipeline_id_cai_no_fallback(self, monkeypatch):
        """Se pipeline_id eh None, nao consulta Mongo — cai no fallback generico."""
        import agents.art_director as ad

        async def should_not_be_called(*a, **kw):
            raise AssertionError("nao deveria consultar analise sem pipeline_id")

        # _obter_analise_ref checa pipeline_id antes de chamar o resto
        result = _run(_short_circuit_sem_avatar(
            SAMPLE_COPY,
            brand_palette={"slug": "linkedin"},
            pipeline_id=None,
            claude_api_key="k",
        ))
        illu = result["prompts"][0]["illustration_description"]
        # Fallback usa ingles "PURE WHITE", prompt com analise usa portugues
        assert "PURE WHITE" in illu


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

    def test_thumbnail_youtube_nunca_short_circuit(self, monkeypatch):
        """RN-005: thumbnail_youtube SEMPRE requer avatar. Mesmo com avatar_mode=sem
        ou brand sem refs com_avatar, o art_director precisa rodar pra dirigir a cena
        com o avatar disponivel (senao Gemini inventa cenario aleatorio)."""
        import factories.imagem_factory as factory_mod

        def fake_load(slug, pool):
            return []  # sem refs em nenhum pool
        monkeypatch.setattr(factory_mod, "_load_ref_docs_by_pool", fake_load)

        brand = {"slug": "linkedin"}
        # Mesmo em avatar_mode=sem, thumbnail nao pula
        assert _todos_slides_viram_sem_avatar("sem", brand, formato="thumbnail_youtube") is False
        # Mesmo em livre com brand sem refs com_avatar
        assert _todos_slides_viram_sem_avatar("livre", brand, formato="thumbnail_youtube") is False
        # Mesmo sem brand_palette
        assert _todos_slides_viram_sem_avatar("sem", None, formato="thumbnail_youtube") is False

    def test_post_unico_com_avatar_sem_segue_regra_normal(self, monkeypatch):
        """Para post_unico, avatar_mode=sem ainda faz short-circuit (comportamento normal)."""
        assert _todos_slides_viram_sem_avatar("sem", None, formato="post_unico") is True
        assert _todos_slides_viram_sem_avatar("sem", None, formato="carrossel") is True


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
