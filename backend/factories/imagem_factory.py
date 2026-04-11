"""Factory de imagem — monta prompts e payloads para Gemini usando PromptComposer (4 camadas).

Todas as leituras de assets (refs + avatares) sao feitas APENAS no MongoDB.
Sem fallback disco — disco eh efemero em deploy cloud.
"""

import base64

from factories.prompt_composer import PromptComposer
from services.brand_prompt_builder import carregar_brand


def _get_mongo_docs(brand_slug: str) -> list[dict]:
    """Carrega todos os docs de brand_assets da marca. Retorna [] se Mongo indisponivel."""
    if not brand_slug:
        return []
    try:
        from data.connections.mongo_connection import get_mongo_db
        db = get_mongo_db()
        if db is None:
            return []
        return list(db["brand_assets"].find({"slug": brand_slug}))
    except Exception:
        return []


def _data_uri_to_raw(data_uri: str) -> str:
    """Extrai o base64 puro de um data URI."""
    return data_uri.split(",")[1] if "," in data_uri else data_uri


def _load_avatars(brand_slug: str) -> list[str]:
    """Carrega fotos de avatar da marca (tudo que NAO eh ref_* e NAO eh __foto__).

    Retorna ate 3 base64. So le do MongoDB.
    """
    avatars = []
    for doc in _get_mongo_docs(brand_slug):
        nome = doc.get("nome", "")
        if nome == "__foto__" or nome.startswith("ref_"):
            continue
        data_uri = doc.get("data_uri", "")
        if data_uri:
            avatars.append(_data_uri_to_raw(data_uri))
    return avatars[:3]


def _nome_match_pool(nome: str, pool: str) -> bool:
    """Verifica se um nome de asset pertence ao pool dado.

    Convencao:
        ref_ca_*  -> pool com_avatar
        ref_sa_*  -> pool sem_avatar
        ref_*     -> pool com_avatar (legado, migra invisivel)
    """
    if pool == "com_avatar":
        if nome.startswith("ref_ca_"):
            return True
        # Legado: ref_ sem sufixo conta como com_avatar
        if nome.startswith("ref_") and not nome.startswith("ref_sa_"):
            return True
        return False
    if pool == "sem_avatar":
        return nome.startswith("ref_sa_")
    return False


def _load_references_by_pool(brand_slug: str, pool: str) -> list[str]:
    """Carrega refs de um pool especifico (com_avatar ou sem_avatar).

    Args:
        brand_slug: slug da marca
        pool: 'com_avatar' | 'sem_avatar'

    Returns:
        Lista de base64 (ate 5 refs do pool). So le do MongoDB.
    """
    if pool not in ("com_avatar", "sem_avatar"):
        return []

    refs = []
    for doc in _get_mongo_docs(brand_slug):
        nome = doc.get("nome", "")
        if not _nome_match_pool(nome, pool):
            continue
        data_uri = doc.get("data_uri", "")
        if data_uri:
            refs.append(_data_uri_to_raw(data_uri))

    return refs[:5]


def _load_all_references(brand_slug: str) -> list[str]:
    """Carrega TODAS as imagens de referencia (ref_*) da marca — ambos os pools.

    Mantido pra compatibilidade com o pipeline atual. Na Fase 3 (refs_selector),
    essa funcao sera substituida por chamadas a `_load_references_by_pool` por pool.
    """
    refs = []
    for doc in _get_mongo_docs(brand_slug):
        nome = doc.get("nome", "")
        if not nome.startswith("ref_"):
            continue
        data_uri = doc.get("data_uri", "")
        if data_uri:
            refs.append(_data_uri_to_raw(data_uri))
    return refs[:5]


def _build_style_instruction(brand_slug: str) -> str:
    """Monta instrução detalhada de estilo a partir da análise salva na marca."""
    brand = carregar_brand(brand_slug) if brand_slug else None
    if not brand:
        return ""

    parts = []

    # Prompt perfeito extraído pela IA (o mais importante)
    analise = brand.get("_analise_referencia", {})
    prompt_perfeito = analise.get("prompt_perfeito") or analise.get("prompt_replicar", "")
    if prompt_perfeito:
        # Limpar instruções de feed/grid/profile — focar no estilo visual de 1 post
        import re
        adapted = prompt_perfeito
        # Remover frases sobre layout de feed/grid/profile
        adapted = re.sub(r'[^.]*(?:feed|grid|grade|3x3|9 posts|seção superior|ícones? circulare?s|highlight|navega[çc][ãa]o|tabs?)[^.]*\.?\s*', '', adapted, flags=re.IGNORECASE)
        adapted = adapted.strip()
        if len(adapted) < 50:
            adapted = prompt_perfeito  # fallback se limpou demais
        parts.append(
            f"=== STYLE INSTRUCTIONS (from reference analysis) ===\n"
            f"CRITICAL: Generate a SINGLE post filling the entire canvas. NO Instagram UI, NO profile header, NO highlights, NO grid. Just ONE post image.\n"
            f"{adapted}"
        )

    # Regras do feed
    regras = analise.get("regras_feed") or brand.get("regras_feed", {})
    if regras:
        regras_text = "\n".join(f"- {v}" for v in regras.values() if v)
        if regras_text:
            parts.append(f"=== FEED RULES ===\n{regras_text}")

    # Visual da marca (estilo_fundo, estilo_texto, etc)
    visual = brand.get("visual", {})
    if visual:
        visual_parts = []
        if visual.get("estilo_fundo"):
            visual_parts.append(f"Background: {visual['estilo_fundo']}")
        if visual.get("estilo_texto"):
            visual_parts.append(f"Typography: {visual['estilo_texto']}")
        if visual.get("estilo_desenho"):
            visual_parts.append(f"Illustrations/decorations: {visual['estilo_desenho']}")
        if visual.get("estilo_card"):
            visual_parts.append(f"Cards: {visual['estilo_card']}")
        if visual.get("regras_extras"):
            visual_parts.append(f"Rules: {visual['regras_extras']}")
        if visual_parts:
            parts.append(f"=== VISUAL IDENTITY ===\n" + "\n".join(visual_parts))

    # Fontes
    fontes = brand.get("fontes", {})
    if fontes.get("titulo"):
        parts.append(f"=== FONTS ===\nTitle font: {fontes['titulo']}\nBody font: {fontes.get('corpo', fontes['titulo'])}")

    # Cores
    cores = brand.get("cores", {})
    if cores.get("fundo"):
        cores_text = ", ".join(f"{k}: {v}" for k, v in cores.items() if v and isinstance(v, str) and (v.startswith("#") or v.startswith("rgba")))
        if cores_text:
            parts.append(f"=== COLOR PALETTE ===\n{cores_text}")

    return "\n\n".join(parts)


def select_model(slide: dict, position: int, total: int) -> str:
    """Pro para capa, codigo e CTA. Flash para content."""
    slide_type = slide.get("type", "content")
    if position == 1 or position == total or slide_type == "code":
        return "gemini-3-pro-image-preview"
    return "gemini-2.5-flash-image"


def build_payload(
    slide: dict,
    position: int,
    total: int,
    foto_criador: str | None = None,
    design_system: str | None = None,
    brand_slug: str | None = None,
    avatar_mode: str = "livre",
    formato: str = "carrossel",
    refs_fixas: dict | None = None,
) -> tuple[str, dict]:
    """Retorna (model, payload) prontos para envio a API Gemini.

    Args:
        refs_fixas: dict com refs pre-sorteadas por pool (resultado de
                    refs_selector.escolher_refs_fixas). Se None, cai
                    em fallback legado (_load_all_references).
    """
    model = select_model(slide, position, total)

    prompt = PromptComposer.compor_prompt_imagem(
        slide, position, total, brand_slug or "", formato=formato
    )

    avatar_images = _load_avatars(brand_slug) if brand_slug else []

    # REGRA DE OURO (Fase 3): selecao fixa de REF1 + REF2 por pool
    from factories.refs_selector import get_refs_do_slide, decidir_pool

    if refs_fixas is None and brand_slug:
        # Fallback: se ninguem passou refs_fixas, gera aqui com pipeline_id generico
        from factories.refs_selector import escolher_refs_fixas
        refs_fixas = escolher_refs_fixas(brand_slug, f"fallback-{brand_slug}")

    refs_slide = get_refs_do_slide(refs_fixas, avatar_mode, position, total) if refs_fixas else None
    ref1_estilo = refs_slide["ref1_estilo"] if refs_slide else None
    ref2_composicao = refs_slide["ref2_composicao"] if refs_slide else None
    pool_atual = decidir_pool(avatar_mode, position, total) if brand_slug else "sem_avatar"

    parts: list[dict] = []

    if ref1_estilo:
        from utils.dimensions import get_prompt_size_str

        # Decidir se este slide vai ter a pessoa (avatar)
        is_capa_ou_cta = (position == 1 or position == total)
        include_avatar = bool(avatar_images) and avatar_mode != "sem" and (
            avatar_mode == "sim" or
            (avatar_mode in ("livre", "capa") and is_capa_ou_cta)
        )
        # Se pool escolhido pra esse slide eh sem_avatar, NAO inclui avatar
        if pool_atual == "sem_avatar":
            include_avatar = False

        # Injeta REF1 (estilo) e REF2 (composicao) na ordem — ordem importa
        parts.append({"inline_data": {"mime_type": "image/png", "data": ref1_estilo}})
        if ref2_composicao and ref2_composicao != ref1_estilo:
            parts.append({"inline_data": {"mime_type": "image/png", "data": ref2_composicao}})

        if include_avatar:
            # Manda TODOS os avatares (ate 3) juntos pra garantir a mesma pessoa
            for av in avatar_images[:3]:
                parts.append({"inline_data": {"mime_type": "image/png", "data": av}})

        # Textos do slide
        headline = slide.get("headline") or slide.get("title", "")
        subline = slide.get("subline") or slide.get("caption", "")
        bullets = slide.get("bullets", [])
        body = "\n".join(f"- {b}" for b in bullets) if bullets else subline

        size_str = get_prompt_size_str(formato)

        # REGRA DE OURO no prompt — REF1 = estilo, REF2 = composicao
        p = f"Create a {size_str} social media image following this GOLDEN RULE:\n\n"
        if ref2_composicao and ref2_composicao != ref1_estilo:
            p += (
                "REFERENCE 1 (STYLE DNA): copy colors, fonts, vibe, doodles from this image. Do NOT copy its layout.\n"
                "REFERENCE 2 (LAYOUT): copy where text lives, image proportions, composition from this image. Do NOT copy its colors.\n"
                "HIERARCHY: layout from REF2 > style from REF1 > new content adapts to both.\n\n"
            )
        else:
            p += (
                "REFERENCE (STYLE+LAYOUT): copy colors, fonts, vibe, doodles, and composition from this image.\n\n"
            )

        if include_avatar:
            num_avatars = min(3, len(avatar_images))
            p += (
                f"The following {num_avatars} photos show the SAME person of this brand from different angles. "
                f"USE THIS SPECIFIC PERSON in the slide — her real face, her real identity, exactly as she looks in those photos. "
                f"Keep her recognizable. New pose/angle ok, but it must clearly be HER.\n\n"
            )
        else:
            p += "NO person, NO face in this image. Focus on text, decorations and background.\n\n"

        # Texto EXATO — proibir inventar
        p += "=== TEXT TO DISPLAY (use EXACTLY this, nothing else) ===\n"
        p += f"HEADLINE: {headline}\n"
        if body:
            p += f"BODY: {body}\n"
        p += "=== END TEXT ===\n\n"
        p += "TEXT RULES: use only the headline and body above. Do NOT invent code, color codes, or lorem ipsum. Spell everything correctly in Portuguese.\n"
        p += "\nNo nudity, no violence."

        parts.append({"text": p})
    else:
        # Sem refs disponiveis — prompt puro
        parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "temperature": 0.9,
        },
    }
    return model, payload
