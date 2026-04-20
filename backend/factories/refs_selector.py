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
- layout_tag: quando o slide tem tipo_layout, REF2 (composicao) prefere
  refs tagueadas com o mesmo layout. REF1 (estilo) ignora a tag.
"""

import random
from typing import TypedDict

from factories.imagem_factory import _load_references_by_pool, _load_ref_docs_by_pool, RefDoc


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


class PoolRefDocs(TypedDict):
    """Docs completos de refs de um pool — usado pra selecao por layout_tag."""
    docs: list[RefDoc]
    default_refs: PoolRefs


class RefsFixasComDocs(TypedDict):
    """Refs fixas + docs completos pra selecao por layout_tag por slide."""
    com_avatar: PoolRefs
    sem_avatar: PoolRefs
    _docs_com: list[RefDoc]
    _docs_sem: list[RefDoc]
    _rng_seed: str


def _escolher_par(pool: list[str], rng: random.Random, single: bool = False) -> PoolRefs:
    """Escolhe refs do pool.

    - single=True: sorteia UMA ref so (REF1==REF2). Evita o "frankenstein" de misturar
      duas refs de estilos diferentes — cada ref ja e template completo (cores + layout).
    - single=False (default): sorteia 2 refs distintas (ou 1 duplicada se pool tem 1).
    """
    if not pool:
        return {"ref1_estilo": None, "ref2_composicao": None}
    if single or len(pool) == 1:
        escolhida = rng.choice(pool)
        return {"ref1_estilo": escolhida, "ref2_composicao": escolhida}
    par = rng.sample(pool, 2)
    return {"ref1_estilo": par[0], "ref2_composicao": par[1]}


def escolher_refs_fixas(brand_slug: str, pipeline_id: str) -> RefsFixasComDocs:
    """Sorteia REF1 (estilo) e REF2 (composicao) pra ambos os pools.

    Retorna tambem os docs completos pra permitir selecao por layout_tag
    por slide (REF2 pode mudar se houver ref tagueada).
    """
    rng = random.Random(f"{brand_slug}:{pipeline_id}")

    docs_com = _load_ref_docs_by_pool(brand_slug, "com_avatar")
    docs_sem = _load_ref_docs_by_pool(brand_slug, "sem_avatar")

    pool_com = [d.b64 for d in docs_com]
    pool_sem = [d.b64 for d in docs_sem]

    return {
        "com_avatar": _escolher_par(pool_com, rng),
        # Slides sem avatar recebem UMA ref so (REF1==REF2). Cada ref da marca ja
        # e template completo (cores + composicao). Misturar 2 refs de estilos
        # diferentes produzia "frankenstein" — Gemini usava cores de uma e layout
        # inventado. Com 1 ref unica, ele e forcado a seguir aquele template inteiro.
        "sem_avatar": _escolher_par(pool_sem, rng, single=True),
        "_docs_com": docs_com,
        "_docs_sem": docs_sem,
        "_rng_seed": f"{brand_slug}:{pipeline_id}",
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


def _escolher_ref2_por_layout(docs: list[RefDoc], tipo_layout: str | None, rng_seed: str, position: int) -> str | None:
    """Tenta encontrar uma ref tagueada com o layout_tag do slide pra usar como REF2.

    Se nao encontrar ref tagueada, retorna None (caller usa a REF2 default).
    """
    if not tipo_layout or not docs:
        return None

    tagueadas = [d for d in docs if d.layout_tag == tipo_layout]
    if not tagueadas:
        return None

    rng = random.Random(f"{rng_seed}:layout:{tipo_layout}:{position}")
    return rng.choice(tagueadas).b64


def get_refs_do_slide(
    refs_fixas: dict,
    avatar_mode: str,
    position: int,
    total: int,
    tipo_layout: str | None = None,
) -> PoolRefs:
    """Retorna REF1/REF2 apropriadas pra esse slide.

    Se o slide tem tipo_layout e existem refs tagueadas com esse layout,
    REF2 (composicao) eh substituida pela ref tagueada. REF1 (estilo)
    permanece fixa pra manter consistencia visual.
    """
    pool_nome = decidir_pool(avatar_mode, position, total)
    refs = refs_fixas[pool_nome]

    # Fallback: se o pool escolhido nao tem refs, tenta o outro
    if refs.get("ref1_estilo") is None:
        pool_alt = "com_avatar" if pool_nome == "sem_avatar" else "sem_avatar"
        refs_alt = refs_fixas[pool_alt]
        if refs_alt.get("ref1_estilo") is not None:
            refs = refs_alt
            pool_nome = pool_alt

    # Tentar substituir REF2 por ref tagueada com o layout do slide
    if tipo_layout and refs.get("ref1_estilo"):
        docs_key = "_docs_com" if pool_nome == "com_avatar" else "_docs_sem"
        docs = refs_fixas.get(docs_key, [])
        rng_seed = refs_fixas.get("_rng_seed", "")
        ref2_layout = _escolher_ref2_por_layout(docs, tipo_layout, rng_seed, position)
        if ref2_layout:
            return {
                "ref1_estilo": refs["ref1_estilo"],
                "ref2_composicao": ref2_layout,
            }

    return refs
