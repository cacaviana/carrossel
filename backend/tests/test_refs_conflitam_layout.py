"""Testes do fix: refs genericas (layout_tag=None) NAO sao ignoradas quando o slide
tem tipo_layout mas nenhuma ref tem tag matching.

Contexto (bug anterior): se o slide tinha tipo_layout='texto' e as refs da marca
todas tinham layout_tag=None, o prompt mandava o Gemini IGNORAR o layout das refs
e seguir so as instrucoes textuais de TIPO DE LAYOUT. Resultado: Gemini ignorava
o padrao visual da marca (ex: fundo branco + card no topo) e gerava fullscreen.

Fix: refs com layout_tag=None sao genericas e sempre valem como guia de layout.
So ha conflito quando TODAS as refs do pool tem tags setadas e NENHUMA bate.
"""

import pytest

from factories.imagem_factory import _refs_conflitam_com_layout, build_payload
from factories.refs_selector import RefDoc


def _refs_fixas(docs_sem=None, docs_com=None, ref1=None, ref2=None):
    """Monta estrutura refs_fixas compativel com o que imagem_factory espera."""
    docs_sem = docs_sem or []
    docs_com = docs_com or []
    return {
        "sem_avatar": {
            "ref1_estilo": ref1 or (docs_sem[0].b64 if docs_sem else None),
            "ref2_composicao": ref2 or (docs_sem[1].b64 if len(docs_sem) > 1 else None),
        },
        "com_avatar": {
            "ref1_estilo": None,
            "ref2_composicao": None,
        },
        "_docs_sem": docs_sem,
        "_docs_com": docs_com,
        "_rng_seed": "test",
    }


class TestRefsConflitamHelper:
    """Validacao pura da regra."""

    def test_sem_tipo_layout_nunca_conflita(self):
        refs = _refs_fixas(docs_sem=[RefDoc(b64="b64-a", layout_tag="texto")])
        assert _refs_conflitam_com_layout(refs, "sem_avatar", None) is False

    def test_sem_refs_no_pool_nunca_conflita(self):
        refs = _refs_fixas(docs_sem=[])
        assert _refs_conflitam_com_layout(refs, "sem_avatar", "texto") is False

    def test_ref_sem_tag_e_generica_nao_conflita(self):
        """Caso LinkedIn: 5 refs todas com layout_tag=None, slide com tipo_layout='texto'."""
        docs = [RefDoc(b64=f"b{i}", layout_tag=None) for i in range(5)]
        refs = _refs_fixas(docs_sem=docs)
        assert _refs_conflitam_com_layout(refs, "sem_avatar", "texto") is False

    def test_qualquer_ref_sem_tag_salva_o_pool(self):
        """Mix: algumas com tag que nao bate, mas UMA sem tag. Nao conflita."""
        docs = [
            RefDoc(b64="b1", layout_tag="lista"),
            RefDoc(b64="b2", layout_tag=None),
            RefDoc(b64="b3", layout_tag="comparativo"),
        ]
        refs = _refs_fixas(docs_sem=docs)
        assert _refs_conflitam_com_layout(refs, "sem_avatar", "texto") is False

    def test_ref_com_tag_que_bate_nao_conflita(self):
        docs = [
            RefDoc(b64="b1", layout_tag="lista"),
            RefDoc(b64="b2", layout_tag="texto"),
        ]
        refs = _refs_fixas(docs_sem=docs)
        assert _refs_conflitam_com_layout(refs, "sem_avatar", "texto") is False

    def test_todas_com_tag_diferente_conflita(self):
        """Caso onde ignorar o layout das refs faz sentido: todas tem tag explicita
        E nenhuma bate. As refs foram cadastradas pra outros layouts."""
        docs = [
            RefDoc(b64="b1", layout_tag="lista"),
            RefDoc(b64="b2", layout_tag="comparativo"),
        ]
        refs = _refs_fixas(docs_sem=docs)
        assert _refs_conflitam_com_layout(refs, "sem_avatar", "texto") is True


class TestBuildPayloadRespeitaRefsGenericas:
    """Teste de integracao do prompt montado — garante que o branch 'IGNORE o layout
    das referencias' NAO eh acionado quando refs sao genericas."""

    @staticmethod
    def _get_prompt_text(payload: dict) -> str:
        """Extrai o bloco de texto do payload Gemini."""
        for part in payload["contents"][0]["parts"]:
            if "text" in part:
                return part["text"]
        return ""

    def test_refs_genericas_com_tipo_layout_nao_ignora_layout_das_refs(self):
        """Cenario do bug: brand tem 5 refs todas com layout_tag=None, slide com
        tipo_layout='texto'. Prompt NAO deve pedir pra ignorar layout das refs."""
        docs = [
            RefDoc(b64="AAAA", layout_tag=None),
            RefDoc(b64="BBBB", layout_tag=None),
        ]
        refs = _refs_fixas(docs_sem=docs)

        slide = {
            "type": "cover",
            "tipo_layout": "texto",
            "headline": "Vibecoding",
            "subline": "o queridinho dos ceos",
        }
        _, payload = build_payload(
            slide, position=1, total=1,
            formato="post_unico",
            refs_fixas=refs,
            brand_slug=None,  # sem brand_slug pra evitar chamar Mongo
        )
        prompt = self._get_prompt_text(payload)
        assert "IGNORE o layout/composicao/estrutura das referencias" not in prompt, (
            "Fix regrediu: refs genericas (layout_tag=None) voltaram a ser ignoradas"
        )
        # E o branch certo deve ter sido ativado: layout da REF2 manda na estrutura
        assert "Layout da REFERENCIA 2 manda na ESTRUTURA" in prompt

    def test_refs_com_tags_conflitantes_ignoram_layout_como_antes(self):
        """Cenario legitimo: todas as refs tem tag explicita diferente do tipo_layout.
        Ai sim o prompt deve manter o comportamento de ignorar o layout das refs.

        Usa position=2/total=3 pra cair direto no pool sem_avatar (sem fallback),
        garantindo que ref2_matches_layout fique False honestamente.
        """
        docs = [
            RefDoc(b64="AAAA", layout_tag="lista"),
            RefDoc(b64="BBBB", layout_tag="comparativo"),
        ]
        refs = _refs_fixas(docs_sem=docs)

        slide = {"type": "content", "tipo_layout": "texto", "headline": "Teste"}
        _, payload = build_payload(
            slide, position=2, total=3,
            formato="carrossel",
            refs_fixas=refs,
            brand_slug=None,
        )
        prompt = self._get_prompt_text(payload)
        assert "IGNORE o layout/composicao/estrutura das referencias" in prompt
