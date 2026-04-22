"""Quando refs e target tem aspect ratios diferentes, o prompt DEVE forcar o Gemini
a gerar no formato target — nao copiar ratio das refs.

Contexto: refs podem ser 16:9 (thumbs) mas slide atual pode ser 4:5, ou vice-versa.
Gemini tende a seguir o ratio das imagens anexadas ignorando aspectRatio do config.
Precisa instrucao explicita "output MUST be X:Y, refs are style guides only".
"""

import pytest

from factories.imagem_factory import build_payload
from factories.refs_selector import RefDoc


def _refs_fixas(b64="refb64"):
    return {
        "com_avatar": {"ref1_estilo": None, "ref2_composicao": None},
        "sem_avatar": {"ref1_estilo": b64, "ref2_composicao": b64},
        "_docs_com": [],
        "_docs_sem": [RefDoc(b64=b64, layout_tag=None, nome="ref_sa_x")],
        "_rng_seed": "t",
    }


def _prompt_text(payload):
    for p in payload["contents"][0]["parts"]:
        if "text" in p:
            return p["text"]
    return ""


class TestPromptForcaAspectRatio:

    def test_thumbnail_prompt_tem_instrucao_forte_de_16x9(self, monkeypatch):
        import factories.imagem_factory as mod
        monkeypatch.setattr(mod, "_load_avatars", lambda slug: ["AVATAR_B64"])
        monkeypatch.setattr(mod, "carregar_brand", lambda s: {"slug": s, "dna": {}, "cores": {}})

        slide = {"type": "cover", "headline": "x", "subline": "y"}
        _, payload = build_payload(
            slide, position=1, total=1,
            brand_slug="x", avatar_mode="sim",
            formato="thumbnail_youtube",
            refs_fixas=_refs_fixas(),
        )
        p = _prompt_text(payload)
        # Instrucao MANDATORY sobre o tamanho final
        assert "MANDATORY" in p
        assert "16:9" in p
        assert "1280x720" in p
        # Refs sao STYLE GUIDES
        assert "STYLE GUIDES ONLY" in p
        # Nao copia ratio
        assert "DO NOT copy the aspect ratio" in p
        # E o aspectRatio do Gemini tb esta 16:9
        assert payload["generationConfig"]["imageConfig"]["aspectRatio"] == "16:9"

    def test_carrossel_prompt_forca_4x5(self, monkeypatch):
        import factories.imagem_factory as mod
        monkeypatch.setattr(mod, "_load_avatars", lambda slug: [])
        monkeypatch.setattr(mod, "carregar_brand", lambda s: {"slug": s, "dna": {}, "cores": {}})

        slide = {"type": "cover", "headline": "x", "subline": "y"}
        _, payload = build_payload(
            slide, position=1, total=1,
            brand_slug="x", avatar_mode="livre",
            formato="carrossel",
            refs_fixas=_refs_fixas(),
        )
        p = _prompt_text(payload)
        assert "4:5" in p
        assert "1080x1350" in p
        assert "MANDATORY" in p

    def test_reels_prompt_forca_9x16(self, monkeypatch):
        import factories.imagem_factory as mod
        monkeypatch.setattr(mod, "_load_avatars", lambda slug: [])
        monkeypatch.setattr(mod, "carregar_brand", lambda s: {"slug": s, "dna": {}, "cores": {}})

        slide = {"type": "cover", "headline": "x", "subline": "y"}
        _, payload = build_payload(
            slide, position=1, total=1,
            brand_slug="x", avatar_mode="livre",
            formato="capa_reels",
            refs_fixas=_refs_fixas(),
        )
        p = _prompt_text(payload)
        assert "9:16" in p
        assert "1080x1920" in p
