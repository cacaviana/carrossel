"""Seletor de REF1 (estilo) + REF2 (composicao) — REGRA DE OURO.

Implementa a selecao fixa por carrossel de duas referencias com papeis
definidos:
    REF1 = ESTILO (cores, tipografia, vibe)
    REF2 = COMPOSICAO (layout, posicao, proporcoes)

Regras:
- Refs FIXAS dentro de um mesmo carrossel (pipeline_id) — todos os slides
  do mesmo pool usam a MESMA REF1/REF2.
- Determinismo: seleção aleatoria mas seedada por pipeline_id — o mesmo
  pipeline sempre pega as mesmas refs (reproduzivel).
- Alternancia: como cada pipeline_id eh diferente, posts diferentes da
  mesma marca vao pegar refs diferentes — "mesma identidade, layout novo".
- REF1 e REF2 podem ser a mesma imagem (fallback se pool tem so 1).
- Se pool vazio, retorna None — quem chama lida com o fallback.
"""

import random
from typing import TypedDict

from factories.imagem_factory import _load_references_by_pool


class PoolRefs(TypedDict):
    """Refs fixas de um pool especifico."""
    ref1_estilo: str | None       # base64 da ref de estilo
    ref2_composicao: str | None   # base64 da ref de composicao


class RefsFixas(TypedDict):
    """Refs fixas por carrossel, ja pre-sorteadas pra ambos os pools.

    No momento da geracao de cada slide, o codigo decide qual pool usar
    baseado em avatar_mode + position e pega a REF1/REF2 ja escolhida.
    """
    com_avatar: PoolRefs
    sem_avatar: PoolRefs


def _escolher_par(pool: list[str], rng: random.Random) -> PoolRefs:
    """Escolhe 2 refs distintas (ou 1 duplicada se pool so tem 1)."""
    if not pool:
        return {"ref1_estilo": None, "ref2_composicao": None}
    if len(pool) == 1:
        return {"ref1_estilo": pool[0], "ref2_composicao": pool[0]}
    # Amostra 2 distintas
    par = rng.sample(pool, 2)
    return {"ref1_estilo": par[0], "ref2_composicao": par[1]}


def escolher_refs_fixas(brand_slug: str, pipeline_id: str) -> RefsFixas:
    """Sorteia REF1 (estilo) e REF2 (composicao) pra ambos os pools.

    Args:
        brand_slug: slug da marca
        pipeline_id: ID unico do pipeline (usado como seed)

    Returns:
        RefsFixas com as duas refs pre-sorteadas pra cada pool.
        Se um pool eh vazio, ref1_estilo e ref2_composicao sao None.
    """
    # Seed deterministica: o mesmo pipeline_id sempre pega as mesmas refs
    rng = random.Random(f"{brand_slug}:{pipeline_id}")

    pool_com = _load_references_by_pool(brand_slug, "com_avatar")
    pool_sem = _load_references_by_pool(brand_slug, "sem_avatar")

    return {
        "com_avatar": _escolher_par(pool_com, rng),
        "sem_avatar": _escolher_par(pool_sem, rng),
    }


def decidir_pool(avatar_mode: str, position: int, total: int) -> str:
    """Decide qual pool de refs usar baseado em avatar_mode + posicao do slide.

    Args:
        avatar_mode: 'sem' | 'capa' | 'livre' | 'sim'
        position: posicao 1-indexed do slide
        total: total de slides no carrossel

    Returns:
        'com_avatar' ou 'sem_avatar'
    """
    if avatar_mode == "sem":
        return "sem_avatar"
    if avatar_mode == "sim":
        return "com_avatar"  # todos com pessoa
    if avatar_mode == "capa":
        # So slide 1 (capa) usa pool com avatar
        return "com_avatar" if position == 1 else "sem_avatar"
    # 'livre': capa + ultimo slide (CTA) com avatar, internos sem
    is_capa_ou_cta = (position == 1 or position == total)
    return "com_avatar" if is_capa_ou_cta else "sem_avatar"


def get_refs_do_slide(
    refs_fixas: RefsFixas,
    avatar_mode: str,
    position: int,
    total: int,
) -> PoolRefs:
    """Retorna REF1/REF2 apropriadas pra esse slide.

    Aplica fallback: se o pool escolhido tem None, tenta o outro pool.
    """
    pool_nome = decidir_pool(avatar_mode, position, total)
    refs = refs_fixas[pool_nome]

    # Fallback: se o pool escolhido nao tem refs, tenta o outro
    if refs.get("ref1_estilo") is None:
        pool_alt = "com_avatar" if pool_nome == "sem_avatar" else "sem_avatar"
        refs_alt = refs_fixas[pool_alt]
        if refs_alt.get("ref1_estilo") is not None:
            return refs_alt

    return refs
