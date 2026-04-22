"""Pass 1 do image_generator: NAO passa avatar. Avatar eh aplicado no Pass 2
(services/avatar_fixer.corrigir_avatar).

Passar avatar no Pass 1 causava:
1. Avatares retrato puxavam o aspect ratio (gerava 4:5 em vez de 16:9 pra thumb)
2. Gemini misturava os 3 avatares em uma face Frankenstein

Pass 2 existe justamente pra trocar o rosto cirurgicamente mantendo composicao.
"""

import pytest

from factories.imagem_factory import build_payload
from factories.refs_selector import RefDoc


def _refs_fixas_so_sem_avatar(b64="ref1-b64"):
    """Simula brand sem refs com_avatar: tudo cai em sem_avatar."""
    return {
        "com_avatar": {"ref1_estilo": None, "ref2_composicao": None},
        "sem_avatar": {"ref1_estilo": b64, "ref2_composicao": b64},
        "_docs_com": [],
        "_docs_sem": [RefDoc(b64=b64, layout_tag=None, nome="ref_sa_x")],
        "_rng_seed": "test",
    }


def _extract_parts(payload: dict) -> tuple[list[dict], str]:
    """Retorna (image_parts, text_prompt) do payload Gemini."""
    images = []
    texts = []
    for part in payload["contents"][0]["parts"]:
        if "inline_data" in part:
            images.append(part)
        elif "text" in part:
            texts.append(part["text"])
    return images, "\n".join(texts)


class TestPass1SemAvatar:

    def test_thumbnail_nao_passa_avatar_no_pass1(self, monkeypatch):
        """Pass 1: so ref(s), sem avatar. Avatar sera aplicado no Pass 2."""
        import factories.imagem_factory as mod
        monkeypatch.setattr(mod, "_load_avatars", lambda slug: ["AVATAR_B64_CARLOS"])
        monkeypatch.setattr(mod, "carregar_brand", lambda slug: {"slug": slug, "dna": {}, "cores": {}})

        slide = {"type": "cover", "headline": "Vibecoding", "subline": "um mundo novo"}
        _, payload = build_payload(
            slide, position=1, total=1,
            brand_slug="linkedin",
            avatar_mode="sim",
            formato="thumbnail_youtube",
            refs_fixas=_refs_fixas_so_sem_avatar(),
        )
        images, prompt = _extract_parts(payload)

        # So a ref, sem avatar
        assert len(images) == 1, f"Esperava 1 imagem (so ref), veio {len(images)}"
        # Sem BRAND PERSON no prompt (nao tem avatar no Pass 1)
        assert "BRAND PERSON" not in prompt

    def test_carrossel_respeita_regra_antiga(self, monkeypatch):
        """Carrossel com pool sem_avatar tambem nao inclui avatar (regra antiga)."""
        import factories.imagem_factory as mod
        monkeypatch.setattr(mod, "_load_avatars", lambda slug: ["AVATAR_B64"])
        monkeypatch.setattr(mod, "carregar_brand", lambda slug: {"slug": slug, "dna": {}, "cores": {}})

        slide = {"type": "content", "headline": "x", "subline": "y"}
        _, payload = build_payload(
            slide, position=2, total=3,
            brand_slug="linkedin",
            avatar_mode="livre",
            formato="carrossel",
            refs_fixas=_refs_fixas_so_sem_avatar(),
        )
        images, _ = _extract_parts(payload)
        assert len(images) == 1  # so a ref, sem avatar

    def test_post_unico_tambem_nao_passa_avatar_no_pass1(self, monkeypatch):
        """Pass 1 nao passa avatar em formato algum. Avatar = Pass 2."""
        import factories.imagem_factory as mod
        monkeypatch.setattr(mod, "_load_avatars", lambda slug: ["AVATAR_B64"])
        monkeypatch.setattr(mod, "carregar_brand", lambda slug: {"slug": slug, "dna": {}, "cores": {}})

        slide = {"type": "cover", "headline": "x", "subline": "y"}
        _, payload = build_payload(
            slide, position=1, total=1,
            brand_slug="x",
            avatar_mode="sim",
            formato="post_unico",
            refs_fixas=_refs_fixas_so_sem_avatar(),
        )
        images, _ = _extract_parts(payload)
        assert len(images) == 1
