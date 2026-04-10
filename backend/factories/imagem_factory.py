"""Factory de imagem — monta prompts e payloads para Gemini usando PromptComposer (4 camadas)."""

import base64
from pathlib import Path

from factories.prompt_composer import PromptComposer
from services.brand_prompt_builder import get_reference_image_path, carregar_brand

def _load_avatars(brand_slug: str) -> list[str]:
    """Carrega fotos de avatar da marca (tudo que NAO e ref_*).
    Busca no MongoDB primeiro, disco como fallback."""
    if not brand_slug:
        return []

    avatars = []
    # MongoDB
    try:
        from data.connections.mongo_connection import get_mongo_db
        db = get_mongo_db()
        if db:
            docs = list(db["brand_assets"].find({"slug": brand_slug}))
            for doc in docs:
                nome = doc.get("nome", "")
                if nome.startswith("ref_") or nome == "__foto__":
                    continue
                data_uri = doc.get("data_uri", "")
                if data_uri:
                    raw = data_uri.split(",")[1] if "," in data_uri else data_uri
                    avatars.append(raw)
    except Exception:
        pass

    # Fallback disco
    if not avatars:
        assets_dir = Path(__file__).parent.parent / "assets" / "brand-assets" / brand_slug
        if assets_dir.exists():
            for f in sorted(assets_dir.iterdir()):
                if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp") and not f.stem.startswith("ref_"):
                    avatars.append(base64.b64encode(f.read_bytes()).decode())
    return avatars[:3]


def _load_all_references(brand_slug: str) -> list[str]:
    """Carrega TODAS as imagens de referência (ref_*) da marca.
    Busca no MongoDB primeiro, disco como fallback."""
    if not brand_slug:
        return []

    refs = []
    # MongoDB
    try:
        from data.connections.mongo_connection import get_mongo_db
        db = get_mongo_db()
        if db:
            docs = list(db["brand_assets"].find({"slug": brand_slug}))
            for doc in docs:
                nome = doc.get("nome", "")
                if not nome.startswith("ref_"):
                    continue
                data_uri = doc.get("data_uri", "")
                if data_uri:
                    raw = data_uri.split(",")[1] if "," in data_uri else data_uri
                    refs.append(raw)
    except Exception:
        pass

    # Fallback disco
    if not refs:
        assets_dir = Path(__file__).parent.parent / "assets" / "brand-assets" / brand_slug
        if assets_dir.exists():
            for f in sorted(assets_dir.glob("ref_*")):
                if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp") and f.stat().st_size >= 50 * 1024:
                    refs.append(base64.b64encode(f.read_bytes()).decode())

    # Referência principal do JSON
    ref_principal = _load_reference_for_brand(brand_slug)
    if ref_principal and ref_principal not in refs:
        refs.insert(0, ref_principal)
    return refs[:5]


def _load_reference_for_brand(brand_slug: str) -> str | None:
    """Carrega imagem de referencia da marca (sem cache — sempre le do disco)."""
    ref_path = get_reference_image_path(brand_slug)
    if ref_path:
        return base64.b64encode(ref_path.read_bytes()).decode()
    return None


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
) -> tuple[str, dict]:
    """Retorna (model, payload) prontos para envio a API Gemini."""
    model = select_model(slide, position, total)

    prompt = PromptComposer.compor_prompt_imagem(
        slide, position, total, brand_slug or "", formato=formato
    )

    slide_type = slide.get("type", "content")

    # Assets da marca baseado no avatar_mode
    from services.brand_prompt_builder import get_brand_assets
    usar_assets = False
    if avatar_mode == "sem":
        usar_assets = False
    elif avatar_mode == "capa":
        usar_assets = (position == 1)  # so na capa
    elif avatar_mode == "sim":
        usar_assets = True  # sempre
    elif avatar_mode == "livre":
        usar_assets = True  # art director decide, manda os assets pra ele ter opcao

    assets = get_brand_assets(brand_slug) if (brand_slug and usar_assets) else []

    parts: list[dict] = []

    # Combinar refs + avatares como assets (como era ontem)
    ref_images = _load_all_references(brand_slug) if brand_slug else []
    avatar_images = _load_avatars(brand_slug) if brand_slug else []
    all_assets = ref_images + avatar_images

    # Se tem refs, prompt CURTO — a imagem de referencia ja define o estilo
    if ref_images:
        import random
        from utils.dimensions import get_dims, get_prompt_size_str

        # Variar ref por slide (cada slide usa uma ref diferente se tiver varias)
        ref = ref_images[(position - 1) % len(ref_images)]
        parts.append({"inline_data": {"mime_type": "image/png", "data": ref}})

        # Avatar separado — so capa e CTA pra nao ficar colagem repetida
        is_capa_ou_cta = (position == 1 or position == total)
        include_avatar = avatar_images and avatar_mode != "sem" and (
            avatar_mode == "sim" or
            (avatar_mode in ("livre", "capa") and is_capa_ou_cta)
        )
        if include_avatar:
            av = random.choice(avatar_images)
            parts.append({"inline_data": {"mime_type": "image/png", "data": av}})

        # Textos do slide
        headline = slide.get("headline") or slide.get("title", "")
        subline = slide.get("subline") or slide.get("caption", "")
        bullets = slide.get("bullets", [])
        body = "\n".join(f"- {b}" for b in bullets) if bullets else subline

        dims = get_dims(formato)
        size_str = get_prompt_size_str(formato)

        # Variacao SO de pose/angulo, nao de estilo
        POSES = [
            "person standing facing camera, confident smile",
            "person slightly turned to the side, natural expression",
            "person from a side profile, looking at camera",
            "person from a lower angle, looking up confidently",
            "person with arms raised, energetic pose",
            "person leaning slightly, casual pose",
            "person centered, warm smile",
        ]
        pose = POSES[(position - 1) % len(POSES)]

        # Prompt rigoroso: MESMO ESTILO da ref, so varia pose da pessoa
        p = f"Create a {size_str} social media image in the EXACT style of the reference image above.\n"
        p += "MUST MATCH: same exact colors, same exact fonts, same exact decorative elements (stickers, badges, doodles), same background style, same overall aesthetic.\n"
        if include_avatar:
            p += f"Include a person — DIFFERENT pose from typical: {pose}. Natural look, not a copy of the reference person.\n"
        else:
            p += "NO person, NO face in this image. Replace where the person would be with decorative elements, badges or illustrations matching the brand style.\n"
        p += f"\nText in the image:\n{headline}"
        if body:
            p += f"\n{body}"
        p += "\n\nNo nudity, no violence. Text must be spelled correctly in Portuguese."

        parts.append({"text": p})

    elif all_assets or assets:
        # Assets sem refs separadas (fallback legado)
        import random
        combined = all_assets if all_assets else assets
        refs = random.sample(combined, min(2, len(combined)))
        for r in refs:
            parts.append({"inline_data": {"mime_type": "image/png", "data": r}})
        avatar_instruction = (
            "Use the characters/person from the reference images in this slide. "
            "Keep the SAME appearance but in new poses related to the topic. "
        )
        parts.append({"text": avatar_instruction + prompt})
    else:
        parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "temperature": 0.9,
        },
    }
    return model, payload
