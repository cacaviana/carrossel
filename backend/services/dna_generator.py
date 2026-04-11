"""Service de geracao de DNA da marca — 4 linhas curtas a partir de uma ref.

Usa Gemini Flash via skill dna_extractor. Camada opaca: orquestra carga da
ref, chamada ao skill e persistencia no brand profile.
"""

import os

from services.brand_prompt_builder import carregar_brand, salvar_brand


async def regenerar_dna(slug: str, imagem_b64: str | None = None) -> dict:
    """Gera DNA a partir de uma imagem de ref e salva no brand profile.

    Args:
        slug: brand slug
        imagem_b64: imagem em base64. Se None, pega a primeira ref do pool
                    com_avatar do brand (ou sem_avatar como fallback).

    Returns:
        dict com 'dna' (os 4 campos) e 'slug'.

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

    # Se nao passou imagem, pega a primeira ref disponivel
    if not imagem_b64:
        from factories.imagem_factory import _load_references_by_pool
        refs = _load_references_by_pool(slug, "com_avatar")
        if not refs:
            refs = _load_references_by_pool(slug, "sem_avatar")
        if not refs:
            raise ValueError(f"Marca '{slug}' nao tem nenhuma referencia visual pra gerar DNA")
        imagem_b64 = refs[0]

    from skills.dna_extractor import extrair_dna
    dna = await extrair_dna(imagem_b64, api_key)

    # Persistir no brand profile
    brand["dna"] = dna
    salvar_brand(slug, brand, overwrite=True)

    return {"slug": slug, "dna": dna}
