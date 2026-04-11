"""Service de geracao de DNA da marca — 4 linhas curtas a partir das refs.

Usa Gemini Flash via skill dna_extractor. Camada opaca: orquestra carga das
refs, chamada ao skill e persistencia no brand profile.

IMPORTANTE: manda TODAS as refs disponiveis (ate 5) pro skill pra extrair
o DNA COMUM da marca, nao cores pontuais de uma foto isolada.
"""

import os

from services.brand_prompt_builder import carregar_brand, salvar_brand


async def regenerar_dna(slug: str, imagem_b64: str | None = None) -> dict:
    """Gera DNA a partir das refs da marca e salva no brand profile.

    Args:
        slug: brand slug
        imagem_b64: imagem unica em base64 (forca uso dessa imagem especifica).
                    Se None, pega TODAS as refs disponiveis pro pool com_avatar
                    (ou sem_avatar como fallback) e analisa juntas pra extrair
                    o DNA COMUM da marca.

    Returns:
        dict com 'dna' (os 4 campos), 'slug' e 'refs_analisadas' (int)

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

    # Decidir quais imagens vao pro skill
    if imagem_b64:
        imagens = [imagem_b64]
    else:
        from factories.imagem_factory import _load_references_by_pool
        imagens = _load_references_by_pool(slug, "com_avatar")
        if not imagens:
            imagens = _load_references_by_pool(slug, "sem_avatar")
        if not imagens:
            raise ValueError(f"Marca '{slug}' nao tem nenhuma referencia visual pra gerar DNA")

    from skills.dna_extractor import extrair_dna
    dna = await extrair_dna(imagens, api_key)

    # Persistir no brand profile
    brand["dna"] = dna
    salvar_brand(slug, brand, overwrite=True)

    return {"slug": slug, "dna": dna, "refs_analisadas": len(imagens)}
