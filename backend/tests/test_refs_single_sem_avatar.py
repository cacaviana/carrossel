"""Slides sem_avatar recebem UMA ref so (REF1==REF2), evitando frankenstein.

Contexto: quando o pool tem refs de estilos diferentes (ex: com card vs sem card),
sortear 2 refs distintas faz o Gemini misturar caracteristicas incompativeis.
Com 1 ref, o modelo e forcado a seguir aquele template inteiro.
"""

import random

from factories.refs_selector import _escolher_par, escolher_refs_fixas, RefDoc


class TestEscolherPar:

    def test_single_false_sorteia_duas_refs_distintas(self):
        pool = [f"ref_{i}" for i in range(5)]
        rng = random.Random(42)
        resp = _escolher_par(pool, rng, single=False)
        assert resp["ref1_estilo"] in pool
        assert resp["ref2_composicao"] in pool
        assert resp["ref1_estilo"] != resp["ref2_composicao"]

    def test_single_true_sempre_retorna_mesma_ref_nas_duas_posicoes(self):
        pool = [f"ref_{i}" for i in range(5)]
        for seed in range(10):
            rng = random.Random(seed)
            resp = _escolher_par(pool, rng, single=True)
            assert resp["ref1_estilo"] == resp["ref2_composicao"], (
                f"Com single=True, REF1 deve ser igual a REF2 (seed={seed})"
            )
            assert resp["ref1_estilo"] in pool

    def test_single_true_pool_vazio_retorna_none(self):
        rng = random.Random(0)
        resp = _escolher_par([], rng, single=True)
        assert resp == {"ref1_estilo": None, "ref2_composicao": None}

    def test_single_true_pool_com_1_ref_funciona(self):
        rng = random.Random(0)
        resp = _escolher_par(["so-uma"], rng, single=True)
        assert resp["ref1_estilo"] == "so-uma"
        assert resp["ref2_composicao"] == "so-uma"

    def test_single_true_deterministico_por_seed(self):
        """Mesmo seed = mesma escolha (importante pro refs_fixas por pipeline)."""
        pool = [f"ref_{i}" for i in range(5)]
        escolhas = [_escolher_par(pool, random.Random(7), single=True)["ref1_estilo"] for _ in range(3)]
        assert len(set(escolhas)) == 1, "Seed fixo deve dar mesma escolha"


class TestEscolherRefsFixas:

    def test_sem_avatar_usa_single_ref(self, monkeypatch):
        """O pool sem_avatar deve sempre retornar REF1==REF2 (single mode)."""
        import factories.refs_selector as rs

        # Mock: brand com 5 refs sem avatar, 0 com avatar
        docs_sem = [RefDoc(b64=f"sem_{i}", layout_tag=None) for i in range(5)]
        monkeypatch.setattr(rs, "_load_ref_docs_by_pool", lambda slug, pool: docs_sem if pool == "sem_avatar" else [])

        resp = escolher_refs_fixas("linkedin", "pipeline-xyz")
        ref1 = resp["sem_avatar"]["ref1_estilo"]
        ref2 = resp["sem_avatar"]["ref2_composicao"]

        assert ref1 is not None
        assert ref1 == ref2, "Pool sem_avatar: REF1 deve ser igual a REF2"

    def test_com_avatar_mantem_2_refs_distintas(self, monkeypatch):
        """O pool com_avatar continua sorteando 2 refs distintas (nao e single)."""
        import factories.refs_selector as rs

        docs_com = [RefDoc(b64=f"com_{i}", layout_tag=None) for i in range(5)]
        monkeypatch.setattr(rs, "_load_ref_docs_by_pool", lambda slug, pool: docs_com if pool == "com_avatar" else [])

        resp = escolher_refs_fixas("linkedin", "pipeline-xyz")
        ref1 = resp["com_avatar"]["ref1_estilo"]
        ref2 = resp["com_avatar"]["ref2_composicao"]

        assert ref1 is not None
        assert ref2 is not None
        assert ref1 != ref2, "Pool com_avatar deve ter 2 refs DISTINTAS"

    def test_pipelines_diferentes_pegam_refs_diferentes_no_sem_avatar(self, monkeypatch):
        """Cada pipeline tem seed diferente -> 1 ref diferente entre posts. Alternancia natural."""
        import factories.refs_selector as rs
        docs_sem = [RefDoc(b64=f"sem_{i}", layout_tag=None) for i in range(5)]
        monkeypatch.setattr(rs, "_load_ref_docs_by_pool", lambda slug, pool: docs_sem if pool == "sem_avatar" else [])

        escolhas = set()
        for pid in ("pipe-A", "pipe-B", "pipe-C", "pipe-D", "pipe-E"):
            resp = escolher_refs_fixas("linkedin", pid)
            escolhas.add(resp["sem_avatar"]["ref1_estilo"])
        # Em 5 pipelines diferentes com pool de 5 refs, esperamos variedade (>=2 distintas)
        assert len(escolhas) >= 2, "Pipelines distintos devem variar a ref escolhida"
