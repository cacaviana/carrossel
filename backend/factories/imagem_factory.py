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


class RefDoc:
    """Ref com metadados (base64 + layout_tag)."""
    __slots__ = ("b64", "layout_tag")

    def __init__(self, b64: str, layout_tag: str | None):
        self.b64 = b64
        self.layout_tag = layout_tag


def _load_references_by_pool(brand_slug: str, pool: str) -> list[str]:
    """Carrega refs de um pool especifico (com_avatar ou sem_avatar).

    Returns:
        Lista de base64 (ate 5 refs do pool). So le do MongoDB.
    """
    return [r.b64 for r in _load_ref_docs_by_pool(brand_slug, pool)]


def _load_ref_docs_by_pool(brand_slug: str, pool: str) -> list[RefDoc]:
    """Carrega refs com metadados de um pool especifico.

    Returns:
        Lista de RefDoc (ate 5 refs do pool). So le do MongoDB.
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
            refs.append(RefDoc(
                b64=_data_uri_to_raw(data_uri),
                layout_tag=doc.get("layout_tag"),
            ))

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
    """Pro em todos os slides — qualidade maxima sempre."""
    return "gemini-3-pro-image-preview"


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
    background_b64: str | None = None,
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
    brand = carregar_brand(brand_slug) if brand_slug else None

    # REGRA DE OURO (Fase 3): selecao fixa de REF1 + REF2 por pool
    from factories.refs_selector import get_refs_do_slide, decidir_pool

    if refs_fixas is None and brand_slug:
        # Fallback: se ninguem passou refs_fixas, gera aqui com pipeline_id generico
        from factories.refs_selector import escolher_refs_fixas
        refs_fixas = escolher_refs_fixas(brand_slug, f"fallback-{brand_slug}")

    tipo_layout = slide.get("tipo_layout")
    refs_slide = get_refs_do_slide(refs_fixas, avatar_mode, position, total, tipo_layout=tipo_layout) if refs_fixas else None
    # Saber se REF2 foi trocada por uma ref tagueada com o layout certo
    ref2_matches_layout = False
    if tipo_layout and refs_fixas and refs_slide:
        pool_nome = decidir_pool(avatar_mode, position, total)
        default_ref2 = refs_fixas[pool_nome].get("ref2_composicao")
        ref2_matches_layout = (refs_slide.get("ref2_composicao") != default_ref2)
    ref1_estilo = refs_slide["ref1_estilo"] if refs_slide else None
    ref2_composicao = refs_slide["ref2_composicao"] if refs_slide else None
    pool_atual = decidir_pool(avatar_mode, position, total) if brand_slug else "sem_avatar"

    parts: list[dict] = []

    # Modo upload: prompt dedicado
    if background_b64:
        from utils.dimensions import get_prompt_size_str, get_dims

        # Detectar modo criativo pelo illustration_description
        illustration = slide.get("illustration_description", "")
        is_criativo = "creative visual elements" in illustration.lower() or "layers" in illustration.lower()

        headline = slide.get("headline") or slide.get("title", "")
        subline = slide.get("subline") or slide.get("caption", "")
        bullets = slide.get("bullets", [])
        body = "\n".join(f"- {b}" for b in bullets) if bullets else subline
        size_str = get_prompt_size_str(formato)

        if is_criativo:
            # MODO CRIATIVO: reproduzir a imagem exata + texto + grafismos da brand
            bg_raw = background_b64.split(",")[1] if "," in background_b64 else background_b64
            parts.append({"inline_data": {"mime_type": "image/png", "data": bg_raw}})

            # Grafismos vem da config da brand
            brand_criativo = carregar_brand(brand_slug) if brand_slug else None
            grafismos_instruction = ""
            if brand_criativo:
                visual_brand = brand_criativo.get("visual", {})
                dna = brand_criativo.get("dna", {})
                cores_brand = brand_criativo.get("cores", {})

                partes_graf = []
                if visual_brand.get("estilo_elemento"):
                    est = visual_brand["estilo_elemento"]
                    if isinstance(est, dict):
                        partes_graf.append(f"Style: {est.get('tipo', '')}, {est.get('linhas', '')}")
                    elif isinstance(est, str):
                        partes_graf.append(f"Style: {est}")
                if visual_brand.get("estilo_desenho"):
                    partes_graf.append(f"Desenho: {visual_brand['estilo_desenho']}")
                if dna.get("elementos"):
                    partes_graf.append(f"Elementos: {dna['elementos']}")
                if cores_brand:
                    cores_hex = [v for k, v in cores_brand.items() if isinstance(v, str) and v.startswith("#")]
                    if cores_hex:
                        partes_graf.append(f"Cores da marca: {', '.join(cores_hex[:6])}")

                if partes_graf:
                    grafismos_instruction = "\n".join(partes_graf)

            from utils.dimensions import get_dims as _get_dims_local
            dims_local = _get_dims_local(formato)

            p = (
                f"Generate the output image at EXACTLY {dims_local['width']}x{dims_local['height']} pixels "
                f"({size_str}). The aspect ratio MUST match — do not output square if target is portrait, "
                f"do not crop or change dimensions.\n\n"
            )

            p += (
                "[REGRA — REPRODUZIR + TEXTO + POUCOS GRAFISMOS]\n"
                "1. REPRODUCE the attached image as faithfully as possible — same scene, same colors, same composition\n"
                "2. OUTPUT must match the target dimensions above (not the dimensions of the attached image)\n"
                "3. ADD the text below in large, bold, legible typography — well positioned\n"
                "4. ADD 1-2 DISCRETE decorative graphic elements near the text or in empty corners — SUBTLE, NOT exaggerated\n"
                "5. Graphics must be SMALL and MINIMAL — a delicate accent, not a design intervention\n"
                "6. DO NOT fill the image with graphics, circuits, lines, or patterns everywhere\n"
                "7. DO NOT cover the main subject with decorations\n"
                "8. DO NOT add faixas, solid bars, banners, boxes, or heavy overlays\n"
                "9. DO NOT add people or avatars\n"
                "10. The original image scene must remain 95% visible and recognizable\n"
                "\n"
            )

            if grafismos_instruction:
                p += (
                    "[ESTILO DOS GRAFISMOS — identidade da marca, aplicar com MODERACAO]\n"
                    f"{grafismos_instruction}\n"
                    "Use this style ONLY for the 1-2 small decorative accents. Do NOT fill the image with this style.\n"
                    "\n"
                )
            else:
                p += (
                    "[GRAFISMOS]\n"
                    "Add 1-2 subtle decorative elements (small lines or dots) near the text. Minimal.\n"
                    "\n"
                )

        else:
            # Outros templates de upload (não deveria chegar aqui, mas fallback seguro)
            bg_raw = background_b64.split(",")[1] if "," in background_b64 else background_b64
            parts.append({"inline_data": {"mime_type": "image/png", "data": bg_raw}})

            p = f"Generate EXACTLY this image as a {size_str} social media post.\n\n"
            p += (
                "[REGRA — REPRODUZIR + TEXTO]\n"
                "1. REPRODUCE the attached image faithfully\n"
                "2. ADD ONLY the text below\n"
                "3. DO NOT add any extra elements\n"
                "\n"
            )

        p += (
            "[TEXTO A EXIBIR — use EXATAMENTE estes textos, nada mais]\n"
            f"HEADLINE: {headline}\n"
        )
        if body:
            p += f"BODY: {body}\n"
        p += (
            "- Nao inventar texto extra\n"
            "- Escrever corretamente em portugues\n"
            "\n"
        )

        p += "No nudity, no violence."

        parts.append({"text": p})

        # Aspect ratio
        dims = get_dims(formato)
        ratio_map = {
            "4:5": "4:5",
            "1:1": "1:1",
            "16:9": "16:9",
            "9:16": "9:16",
        }
        gemini_ratio = ratio_map.get(dims.get("ratio", "4:5"), "4:5")

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "responseModalities": ["IMAGE", "TEXT"],
                "temperature": 0.9,
                "imageConfig": {
                    "aspectRatio": gemini_ratio,
                },
            },
        }
        return model, payload

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
        tem_2_refs = bool(ref2_composicao and ref2_composicao != ref1_estilo)
        if tem_2_refs:
            parts.append({"inline_data": {"mime_type": "image/png", "data": ref2_composicao}})

        num_refs_style = 2 if tem_2_refs else 1
        num_avatars = 0
        if include_avatar:
            num_avatars = min(3, len(avatar_images))
            for av in avatar_images[:num_avatars]:
                parts.append({"inline_data": {"mime_type": "image/png", "data": av}})

        # Textos do slide
        headline = slide.get("headline") or slide.get("title", "")
        subline = slide.get("subline") or slide.get("caption", "")
        bullets = slide.get("bullets", [])
        body = "\n".join(f"- {b}" for b in bullets) if bullets else subline

        size_str = get_prompt_size_str(formato)

        # DNA resumido (4 linhas curtas) pro bloco [ESTILO]
        dna = (brand.get("dna") or {}) if brand else {}
        dna_block = ""
        if dna:
            estilo_dna = dna.get("estilo", "")
            cores_dna = dna.get("cores", "")
            tipo_dna = dna.get("tipografia", "")
            elem_dna = dna.get("elementos", "")
            dna_parts = []
            if estilo_dna: dna_parts.append(f"- estilo: {estilo_dna}")
            if cores_dna: dna_parts.append(f"- cores: {cores_dna}")
            if tipo_dna: dna_parts.append(f"- tipografia: {tipo_dna}")
            if elem_dna: dna_parts.append(f"- elementos: {elem_dna}")
            if dna_parts:
                dna_block = "\n".join(dna_parts)

        # Illustration_description do art_director (cena desenhada pro slide)
        illustration = slide.get("illustration_description", "")

        # === PROMPT MONTADO — estrutura validada pelo usuario ===
        p = f"Create a {size_str} social media image.\n\n"

        # === IMAGENS ANEXADAS (map de ordem pra Gemini saber o que eh cada uma)
        if include_avatar:
            p += (
                f"=== IMAGES ATTACHED ({num_refs_style + num_avatars} total) ===\n"
                f"- Image 1 = REFERENCIA 1 (ESTILO): cores, tipografia, iluminacao, textura, vibe\n"
            )
            if tem_2_refs:
                p += f"- Image 2 = REFERENCIA 2 (LAYOUT): estrutura, composicao, posicao dos elementos\n"
            start = num_refs_style + 1
            end = num_refs_style + num_avatars
            p += f"- Images {start} to {end} = BRAND PERSON (fotos da pessoa real da marca)\n\n"
        else:
            p += (
                f"=== IMAGES ATTACHED ({num_refs_style} total) ===\n"
                f"- Image 1 = REFERENCIA 1 (ESTILO): cores, tipografia, iluminacao, textura, vibe\n"
            )
            if tem_2_refs:
                p += f"- Image 2 = REFERENCIA 2 (LAYOUT): estrutura, composicao, posicao dos elementos\n"
            p += "\n"

        # === REGRA DE HIERARQUIA — muda conforme tem ref de layout ou nao
        if tipo_layout and not ref2_matches_layout:
            # SEM ref tagueada pro layout: refs sao SO pra estilo, layout vem do tipo_layout
            p += (
                "[REGRA DE HIERARQUIA - OBRIGATORIA]\n"
                "1. TODAS as referencias anexadas servem APENAS para APARENCIA: cores, tipografia, iluminacao, textura, vibe, elementos decorativos\n"
                "2. IGNORE o layout/composicao/estrutura das referencias — NAO copie como elas organizam cards, colunas, blocos ou posicao de texto\n"
                "3. A COMPOSICAO deste slide segue EXCLUSIVAMENTE as instrucoes de [TIPO DE LAYOUT] abaixo\n"
                "4. Conteudo NOVO — nao copia elementos literais de nenhuma referencia\n"
                "\n"
            )
        elif tem_2_refs:
            p += (
                "[REGRA DE HIERARQUIA - OBRIGATORIA]\n"
                "1. Layout da REFERENCIA 2 manda na ESTRUTURA (divisao do espaco, alinhamento, proporcao, onde fica texto vs imagem)\n"
                "2. Estilo da REFERENCIA 1 manda na APARENCIA (cores, estetica, luz, textura)\n"
                "3. Conteudo NOVO adapta aos dois — nao copia elementos literais de nenhuma\n"
                "\n"
            )
        else:
            p += (
                "[REGRA DE HIERARQUIA - OBRIGATORIA]\n"
                "1. Layout e composicao seguem a REFERENCIA (divisao, alinhamento, proporcao)\n"
                "2. Estilo da REFERENCIA 1 manda na APARENCIA (cores, estetica, luz, textura)\n"
                "3. Conteudo NOVO adapta aos dois — nao copia elementos literais de nenhuma\n"
                "\n"
            )

        # === ANTI-COPIA
        p += (
            "[ANTI-COPIA — REGRAS ABSOLUTAS]\n"
            "- PROIBIDO replicar a cena original das referencias\n"
            "- PROIBIDO copiar objetos especificos (xicaras, livros, roupas, props)\n"
            "- PROIBIDO copiar pose identica ou expressao identica\n"
            "- PROIBIDO copiar composicao exata (mesma divisao de cards, mesma moldura)\n"
            "- O resultado deve ser uma NOVA imagem INSPIRADA no estilo, nao uma copia\n"
            "- NAO misturar as imagens de referencia entre si\n"
            "- NAO distorcer rostos nem texto — priorizar legibilidade\n"
            "\n"
        )

        # === ESTILO (DNA)
        if dna_block:
            p += (
                "[ESTILO — DNA da marca]\n"
                f"{dna_block}\n"
                "\n"
            )

        # === BRAND PERSON (avatar) — overrides anti-copia de pessoa
        if include_avatar:
            p += (
                f"[BRAND PERSON — excecao a regra anti-copia]\n"
                f"As {num_avatars} ultimas imagens anexadas sao da pessoa real da marca. "
                f"USE essa pessoa no slide — mesmo rosto, mesma identidade, mesmo cabelo, mesma idade, mesmo genero. "
                f"Ela DEVE ser reconhecivel. Nova pose/angulo/contexto OK, mas a face eh INSTANTANEAMENTE a mesma das fotos.\n"
                f"Se a REFERENCIA 1 ou 2 mostrar a MESMA pessoa, tudo bem — use as fotos BRAND PERSON como fonte da verdade pra rosto, e as referencias so pra estilo/layout.\n"
                f"\n"
            )
        else:
            p += "[SEM PESSOA] Este slide NAO deve ter pessoa nem rosto. Foco em objetos, cenario, texto e decoracoes.\n\n"

        # === TIPO DE LAYOUT (guia a composicao visual do conteudo)
        layout_instructions = {
            "texto": (
                "COMPOSICAO OBRIGATORIA — TEXTO SIMPLES:\n"
                "- Headline grande e centralizada, ocupando ~40% do slide\n"
                "- Paragrafo de apoio abaixo em fonte menor\n"
                "- Composicao LIMPA: sem cards, sem colunas, sem baloes, sem setas\n"
                "- Fundo com textura/gradiente sutil da marca, texto direto sobre ele\n"
                "- Hierarquia: 1 texto grande + 1 texto pequeno, nada mais"
            ),
            "lista": (
                "COMPOSICAO OBRIGATORIA — LISTA / BULLET POINTS:\n"
                "- Titulo no topo (~20% do slide)\n"
                "- Abaixo: 3 a 6 itens em COLUNA VERTICAL, alinhados a esquerda\n"
                "- Cada item tem um marcador visual (bolinha, icone, numero) + texto ao lado\n"
                "- PROIBIDO: baloes conectados por setas, cards flutuantes, layouts circulares\n"
                "- Os itens devem parecer uma LISTA REAL — como bullet points de uma apresentacao\n"
                "- Espacamento generoso e uniforme entre cada item\n"
                "- Fundo limpo, sem distracao visual entre os itens"
            ),
            "comparativo": (
                "COMPOSICAO OBRIGATORIA — COMPARATIVO (X vs Y):\n"
                "- Titulo centralizado no topo\n"
                "- DOIS BLOCOS lado a lado ocupando ~80% do slide\n"
                "- Divisor visual claro no centro (linha, vs, ou espacamento)\n"
                "- Bloco ESQUERDO: label + itens do lado A\n"
                "- Bloco DIREITO: label + itens do lado B\n"
                "- PROIBIDO: lista unica, bullets em coluna, layout vertical sem divisao\n"
                "- Os dois lados devem ter CONTRASTE VISUAL (cor diferente, fundo diferente)\n"
                "- O leitor deve entender INSTANTANEAMENTE que sao dois lados sendo comparados"
            ),
            "dados": (
                "COMPOSICAO OBRIGATORIA — DADOS / NUMEROS EM DESTAQUE:\n"
                "- Titulo no topo\n"
                "- NUMEROS/METRICAS em tamanho 3x maior que texto normal\n"
                "- Cada metrica em seu proprio card ou bloco destacado\n"
                "- Layout: 2 a 4 stat cards em grid (2x2 ou 1x3)\n"
                "- PROIBIDO: bullets simples, lista corrida, texto corrido sem destaque numerico\n"
                "- Cada numero deve ter: valor grande + label pequeno abaixo ou ao lado\n"
                "- Cores de destaque nos numeros (acento da marca)\n"
                "- O leitor deve VER OS NUMEROS PRIMEIRO, texto depois"
            ),
        }
        if tipo_layout and tipo_layout in layout_instructions:
            force_label = "" if ref2_matches_layout else " — ESTA INSTRUCAO TEM PRIORIDADE SOBRE AS REFERENCIAS"
            p += (
                f"[TIPO DE LAYOUT — {tipo_layout.upper()}{force_label}]\n"
                f"{layout_instructions[tipo_layout]}\n"
                "\n"
            )

        # === CENA (illustration_description do art_director)
        if illustration:
            p += (
                "[CENA A RENDERIZAR — direcao do art director]\n"
                f"{illustration}\n"
                "\n"
            )

        # === TEXTO EXATO (nunca inventar)
        p += (
            "[TEXTO A EXIBIR — use EXATAMENTE estes textos, nada mais]\n"
            f"HEADLINE: {headline}\n"
        )
        if body:
            p += f"BODY: {body}\n"
        p += (
            "- Nao inventar codigo, color codes, lorem ipsum ou texto extra\n"
            "- Escrever corretamente em portugues\n"
            "\n"
        )

        # === RODAPE / CONTADOR — bloquear clone das refs
        p += (
            "[RODAPE — REGRA ABSOLUTA]\n"
            "- ZERO contadores de slide (ex: 1/3, 2/7)\n"
            "- ZERO numeros de pagina\n"
            "- ZERO circulos com numeros dentro\n"
            "- As referencias podem ter contadores no rodape — IGNORE isso\n"
            "- Rodape vazio ou apenas com o nome da marca\n"
            "\n"
        )

        p += "No nudity, no violence."

        parts.append({"text": p})
    else:
        # Sem refs disponiveis — prompt puro
        parts.append({"text": prompt})

    # Aspect ratio via imageConfig — Gemini ignora hints no texto do prompt.
    # Mapeia formato -> ratio Gemini (suporta 1:1, 3:4, 4:3, 9:16, 16:9, 4:5, 5:4).
    from utils.dimensions import get_dims
    dims = get_dims(formato)
    ratio_map = {
        "4:5": "4:5",      # carrossel LinkedIn portrait
        "1:1": "1:1",      # post unico
        "16:9": "16:9",    # thumbnail youtube
        "9:16": "9:16",    # reels
    }
    gemini_ratio = ratio_map.get(dims.get("ratio", "4:5"), "4:5")

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "temperature": 0.9,
            "imageConfig": {
                "aspectRatio": gemini_ratio,
            },
        },
    }
    return model, payload
