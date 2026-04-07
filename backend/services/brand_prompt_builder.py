"""Gera prompts de imagem a partir do Brand Profile (design system por marca).

Cada marca tem seu visual configuravel em assets/design-systems/{slug}.json.
O prompt e montado dinamicamente a partir do perfil visual da marca.
"""

import json
from pathlib import Path

from utils.dimensions import get_dims, get_prompt_size_str

DS_DIR = Path(__file__).parent.parent / "assets" / "design-systems"


def carregar_brand(slug: str) -> dict | None:
    """Carrega brand profile do JSON. Sempre le do disco (sem cache)."""
    path = DS_DIR / f"{slug}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def salvar_brand(slug: str, data: dict, overwrite: bool = False) -> dict:
    """Salva brand profile no JSON."""
    path = DS_DIR / f"{slug}.json"
    if path.exists() and not overwrite:
        raise FileExistsError(f"Marca '{slug}' ja existe")
    DS_DIR.mkdir(parents=True, exist_ok=True)
    data["slug"] = slug
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def deletar_brand(slug: str) -> bool:
    """Deleta brand profile."""
    path = DS_DIR / f"{slug}.json"
    if not path.exists():
        return False
    path.unlink()
    return True


def listar_brands() -> list[dict]:
    """Lista todas as marcas disponiveis."""
    brands = []
    for path in sorted(DS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            brands.append({
                "slug": data.get("slug", path.stem),
                "nome": data.get("nome", path.stem),
            })
        except Exception:
            continue
    return brands


def build_design_system_text(brand: dict) -> str:
    """Monta a descricao do design system completa a partir do brand profile."""
    import random
    cores = brand.get("cores", {})
    visual = brand.get("visual", {})
    elementos = brand.get("elementos", {})

    partes = []

    # Fundo
    partes.append(visual.get("estilo_fundo", ""))

    # Cores
    partes.append(
        f"Cores: principal {cores.get('acento_principal', '')}, "
        f"secundario {cores.get('acento_secundario', '')}, "
        f"terciario {cores.get('acento_terciario', '')}, "
        f"negativo {cores.get('acento_negativo', '')}. "
        f"Texto: {cores.get('texto_principal', '')} (principal), "
        f"{cores.get('texto_secundario', '')} (secundario). "
        f"Card: {cores.get('card', '')} com borda {cores.get('card_borda', '')}."
    )

    # Elemento decorativo (wireframe, holograma, etc)
    elem = visual.get("estilo_elemento", {})
    if isinstance(elem, dict) and elem:
        partes.append(
            f"ELEMENTO DECORATIVO: tipo={elem.get('tipo', '')}. "
            f"Linhas: {elem.get('linhas', '')}. "
            f"Complexidade: {elem.get('complexidade', '')}. "
            f"Profundidade: {elem.get('profundidade', '')}. "
            f"Opacidade: {elem.get('opacidade', '')}. "
            f"TEMATICO: {elem.get('tematico', '')}."
        )
    elif isinstance(elem, str) and elem:
        partes.append(f"ELEMENTO DECORATIVO: {elem}")

    # Posicionamento do elemento
    pos = visual.get("posicionamento_elemento", {})
    if isinstance(pos, dict) and pos:
        partes.append(
            f"POSICIONAMENTO DO ELEMENTO: {pos.get('regra', '')}. "
            f"Capa: {pos.get('capa', '')}. "
            f"Conteudo: {pos.get('conteudo', '')}. "
            f"CTA: {pos.get('cta', '')}."
        )

    # Card
    partes.append(visual.get("estilo_card", ""))

    # Texto
    partes.append(visual.get("estilo_texto", ""))

    # Badges
    badges = visual.get("badges", {})
    if isinstance(badges, dict) and badges:
        partes.append(
            f"BADGES: capa={badges.get('capa', '')}, "
            f"codigo={badges.get('codigo', '')}, "
            f"categoria={badges.get('categoria', '')}."
        )

    # Rodape
    rodape = visual.get("rodape", {})
    if isinstance(rodape, dict) and rodape:
        partes.append(f"RODAPE: {rodape.get('formato', '')}.")

    # Slide de codigo
    cod = visual.get("slide_codigo", {})
    if isinstance(cod, dict) and cod:
        partes.append(
            f"SLIDE DE CODIGO: janela {cod.get('janela', '')}, "
            f"corpo {cod.get('corpo', '')}."
        )

    # Regras extras
    partes.append(visual.get("regras_extras", ""))

    # Regra de texto
    partes.append(
        "REGRA CRITICA: O texto fornecido DEVE ser renderizado "
        "EXATAMENTE como esta escrito, letra por letra. "
        "NAO alterar, NAO traduzir, NAO adicionar texto extra."
    )

    # Seed aleatorio
    partes.append(f"[seed:{random.randint(1000,9999)}]")

    return " ".join(p for p in partes if p)


def _rodape_instruction(elementos: dict, counter: str, brand_slug: str | None = None) -> str:
    """Monta instrucao do rodape baseado em ter foto ou nao."""
    from pathlib import Path
    nome = elementos.get("rodape_nome", "")

    # Checar se tem foto cadastrada
    tem_foto = False
    if brand_slug:
        fotos_dir = Path(__file__).parent.parent / "assets" / "fotos"
        for ext in ("jpg", "png", "jpeg"):
            if (fotos_dir / f"{brand_slug}.{ext}").exists():
                tem_foto = True
                break

    return f"Rodape: apenas texto '{nome}' + '{counter}' no canto inferior."


def build_prompt(slide: dict, position: int, total: int, brand_slug: str = "", formato: str = "carrossel") -> str:
    """DEPRECATED: usar PromptComposer. Ver factories/prompt_composer.py

    Constroi prompt completo a partir do brand profile + tipo do slide.
    """
    size_str = get_prompt_size_str(formato)
    dims = get_dims(formato)
    ratio = dims["ratio"]

    brand = carregar_brand(brand_slug) if brand_slug else None
    if not brand:
        # Tentar primeiro brand disponivel
        brands = listar_brands()
        if brands:
            brand = carregar_brand(brands[0]["slug"])
    if not brand:
        return f"Create a social media slide ({size_str}). Title: \"{slide.get('headline') or slide.get('title', '')}\" Professional style."

    ds = build_design_system_text(brand)
    visual = brand.get("visual", {})
    elementos = brand.get("elementos", {})
    cores = brand.get("cores", {})
    slide_type = slide.get("type", "content")
    counter = f"{position}/{total}"

    # Thumbnail YouTube — avatar GRANDE 40% da tela
    if formato == "thumbnail_youtube":
        from services.prompt_templates import FOTO_INSTRUCTION_THUMBNAIL
        headline = slide.get("headline", "") or slide.get("title", "") or slide.get("titulo", "")
        if not headline:
            for el in slide.get("elementos", []):
                if "titulo" in el.get("tipo", ""):
                    h = el.get("texto", el.get("conteudo", ""))
                    headline = " ".join(x.get("texto", "") if isinstance(x, dict) else str(x) for x in h) if isinstance(h, list) else h
                    break
        if not headline:
            headline = slide.get("subline", "") or slide.get("corpo", "") or "TECH"
        principal = cores.get("acento_principal", "#A78BFA")
        fundo = cores.get("fundo", "#0A0A0F")
        return (
            f"YouTube thumbnail, {ratio} horizontal landscape ({size_str}). "
            f"RIGHT SIDE (40%) = {FOTO_INSTRUCTION_THUMBNAIL} "
            f"LEFT SIDE (60%) = HUGE bold text: '{headline}' in white with dark outline. "
            f"Background: vibrant gradient using brand colors {principal} and {fundo}. "
            f"High contrast, eye-catching, modern YouTube 2025 style. "
            f"ONLY two elements: creator's face + big text. Nothing else."
        )

    # Illustration override
    illustration = slide.get("illustration_description", "")
    if illustration:
        return _visual_prompt(slide, counter, ds, illustration, visual, size_str, ratio)

    rodape = _rodape_instruction(elementos, counter, brand_slug)

    if slide_type == "cover":
        return _cover_prompt(slide, ds, visual, elementos, cores, rodape, size_str, ratio)
    if slide_type == "cta":
        return _cta_prompt(slide, ds, visual, elementos, cores, counter, rodape, brand_slug, size_str, ratio)
    if slide_type == "code":
        return _code_prompt(slide, counter, ds, visual, cores, rodape, size_str, ratio)
    if slide_type == "comparison":
        return _comparison_prompt(slide, counter, ds, visual, cores, rodape, size_str, ratio)
    return _content_prompt(slide, counter, ds, visual, elementos, cores, rodape, size_str, ratio)


def _cover_prompt(slide, ds, visual, elementos, cores, rodape, size_str="1080x1350px, 4:5 portrait", ratio="4:5"):
    headline = slide.get("headline", "")
    subline = slide.get("subline", "")
    badge = elementos.get("badge_topo", "")
    badge_cor = elementos.get("badge_topo_cor", cores.get("acento_secundario", ""))
    desenho = visual.get("estilo_desenho", "")

    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). {ds} "
        f"Badge pill ({badge_cor}) no topo: '{badge}'. "
        f"Headline ENORME em {cores.get('texto_principal', 'branco')}, "
        f"com palavras-chave em {cores.get('acento_principal', '')} bold: '{headline}'. "
        f"Subline em {cores.get('texto_secundario', 'cinza')}: '{subline}'. "
        f"Na parte inferior: {desenho} "
        f"{rodape} TODO texto LEGIVEL."
    )


def _content_prompt(slide, counter, ds, visual, elementos, cores, rodape, size_str="1080x1350px, 4:5 portrait", ratio="4:5"):
    title = slide.get("title", "")
    etapa = slide.get("etapa", "")
    bullets = slide.get("bullets", [])
    bullets_text = "\n".join(f"- {b}" for b in bullets)
    desenho = visual.get("estilo_desenho", "")

    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). {ds} "
        f"Card central GRANDE com o estilo definido pelo design system. "
        f"Badge pill {cores.get('acento_principal', '')} no topo do card: '{etapa}'. "
        f"Titulo GRANDE em {cores.get('texto_principal', 'branco')} bold: '{title}'. "
        f"Bullets em {cores.get('texto_secundario', 'cinza')}, "
        f"palavras-chave em negrito ou {cores.get('acento_principal', '')}:\n{bullets_text}\n"
        f"No fundo atras do card: {desenho} "
        f"{rodape} Texto LEGIVEL."
    )


def _code_prompt(slide, counter, ds, visual, cores, rodape, size_str="1080x1350px, 4:5 portrait", ratio="4:5"):
    code = slide.get("code", "")
    caption = slide.get("caption", "")
    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). {ds} "
        f"Badge pill {cores.get('acento_secundario', '')} no topo: 'CODIGO REAL'. "
        f"Janela de terminal estilo macOS: barra com 3 botoes (vermelho, amarelo, verde), "
        f"corpo escuro com codigo em {cores.get('acento_secundario', 'verde')}. "
        f"CADA CARACTERE deve ser LEGIVEL. "
        f"Codigo:\n{code}\n"
        f"Caption: '{caption}'. "
        f"{rodape}"
    )


def _comparison_prompt(slide, counter, ds, visual, cores, rodape, size_str="1080x1350px, 4:5 portrait", ratio="4:5"):
    left_label = slide.get("left_label", "")
    right_label = slide.get("right_label", "")
    left_items = slide.get("left_items", [])
    right_items = slide.get("right_items", [])
    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). {ds} "
        f"Card central com dois blocos lado a lado. "
        f"Esquerdo ({cores.get('acento_negativo', 'vermelho')}): '{left_label}' — {', '.join(left_items)}. "
        f"Direito ({cores.get('acento_principal', 'roxo')}): '{right_label}' — {', '.join(right_items)}. "
        f"{rodape}"
    )


def _cta_prompt(slide, ds, visual, elementos, cores, counter, rodape, brand_slug=None, size_str="1080x1350px, 4:5 portrait", ratio="4:5"):
    headline = slide.get("headline", "")
    subline = slide.get("subline", "")
    tags = slide.get("tags", [])
    tags_text = ", ".join(tags)
    desenho = visual.get("estilo_desenho", "")

    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). {ds} "
        f"Headline GRANDE em {cores.get('texto_principal', 'branco')} bold: '{headline}'. "
        f"Texto em {cores.get('texto_secundario', 'cinza')}: '{subline}'. "
        f"Tags em badges pill: {tags_text}. "
        f"{desenho} sutil no fundo. "
        f"Rodape: '{elementos.get('rodape_nome', '')} — {elementos.get('rodape_instituicao', '')} — "
        f"{elementos.get('rodape_extra', '')}'. "
        f"Atmosfera premium."
    )


def _visual_prompt(slide, counter, ds, illustration, visual, size_str="1080x1350px, 4:5 portrait", ratio="4:5"):
    title = slide.get("title", slide.get("headline", ""))
    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). {ds} "
        f"Titulo em destaque: '{title}'. "
        f"A MAIOR PARTE DO SLIDE deve ser ocupada por: {illustration} "
    )


def get_brand_assets(brand_slug: str) -> list[str]:
    """Retorna lista de base64 dos assets da marca."""
    import base64
    assets_dir = DS_DIR.parent / "brand-assets" / brand_slug
    if not assets_dir.exists():
        return []
    assets = []
    for f in sorted(assets_dir.glob("*.*")):
        if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            assets.append(base64.b64encode(f.read_bytes()).decode())
    return assets


def get_reference_image_path(brand_slug: str) -> Path | None:
    """Retorna path da imagem de referencia da marca, se existir."""
    brand = carregar_brand(brand_slug)
    if not brand:
        return None
    ref = brand.get("referencia_imagem")
    if not ref:
        return None
    ref_path = Path(__file__).parent.parent / "assets" / ref
    if ref_path.exists():
        return ref_path
    return None
