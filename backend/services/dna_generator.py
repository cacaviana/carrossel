"""Service de geracao de DNA da marca — 4 linhas curtas a partir das refs.

Usa Gemini Flash via skill dna_extractor. Camada opaca: orquestra carga das
refs, chamada ao skill e persistencia no brand profile.

IMPORTANTE: manda TODAS as refs disponiveis (ate 5) pro skill pra extrair
o DNA COMUM da marca, nao cores pontuais de uma foto isolada.
"""

import os

from services.brand_prompt_builder import carregar_brand, salvar_brand


async def regenerar_dna(slug: str, imagem_b64: str | None = None) -> dict:
    """Gera DNA + padrao_visual separado por pool (com_avatar e sem_avatar).

    Args:
        slug: brand slug
        imagem_b64: imagem unica em base64 (forca uso dessa imagem especifica
                    como se fosse pool unico — nao separa por pool).
                    Se None, analisa cada pool disponivel separadamente e
                    salva padrao_visual.com_avatar e padrao_visual.sem_avatar.

    Returns:
        dict com 'dna' (4 campos curtos), 'padrao_visual' ({com_avatar, sem_avatar}),
        'slug' e 'refs_analisadas' ({com_avatar: int, sem_avatar: int}).

    Raises:
        ValueError: se marca nao existe ou nao tem ref disponivel
        RuntimeError: se GEMINI_API_KEY nao esta configurada
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY nao configurada")

    brand = carregar_brand(slug)
    if not brand:
        raise ValueError(f"Marca '{slug}' nao encontrada")

    from skills.dna_extractor import extrair_dna

    # Modo imagem unica — mantem comportamento legado
    if imagem_b64:
        dna_full = await extrair_dna([imagem_b64], api_key)
        padrao_visual = dna_full.pop("padrao_visual", None)
        brand["dna"] = dna_full
        if padrao_visual:
            brand["padrao_visual"] = padrao_visual
        salvar_brand(slug, brand, overwrite=True)
        return {
            "slug": slug,
            "dna": dna_full,
            "padrao_visual": padrao_visual,
            "refs_analisadas": {"unica": 1},
        }

    # Modo pool separado — analisa com_avatar e sem_avatar independente
    from factories.imagem_factory import _load_references_by_pool

    padrao_visual_por_pool: dict = {}
    refs_analisadas: dict = {}
    dna_curto: dict | None = None

    for pool in ("com_avatar", "sem_avatar"):
        imagens_pool = _load_references_by_pool(slug, pool)
        refs_analisadas[pool] = len(imagens_pool)
        if not imagens_pool:
            continue
        dna_pool = await extrair_dna(imagens_pool, api_key)
        padrao_visual_por_pool[pool] = dna_pool.get("padrao_visual") or {}
        # DNA curto fica do primeiro pool que rolou — vale pra backcompat do prompt composer
        if dna_curto is None:
            dna_curto = {
                "estilo": dna_pool.get("estilo", ""),
                "cores": dna_pool.get("cores", ""),
                "tipografia": dna_pool.get("tipografia", ""),
                "elementos": dna_pool.get("elementos", ""),
            }

    if not padrao_visual_por_pool:
        raise ValueError(f"Marca '{slug}' nao tem nenhuma referencia visual pra gerar DNA")

    brand["dna"] = dna_curto or {}
    brand["padrao_visual"] = padrao_visual_por_pool
    salvar_brand(slug, brand, overwrite=True)

    return {
        "slug": slug,
        "dna": dna_curto,
        "padrao_visual": padrao_visual_por_pool,
        "refs_analisadas": refs_analisadas,
    }
