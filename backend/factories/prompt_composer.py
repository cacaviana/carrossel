"""Factory central de composicao de prompts — junta as 4 camadas.

Camadas (nesta ordem):
1. Seguranca  — regras inviolaveis (import de models.prompt_layer)
2. Plataforma — dimensoes + layout rules do formato
3. Marca      — cores, visual, elementos (imagem) ou persona, tom, hooks (texto)
4. Post       — dados especificos do slide (cover, content, code, comparison, cta, thumbnail)

Regras IT Valley:
- Factory contem regras de negocio (validacoes, invariantes).
- Nenhum arquivo existente e alterado — este e um arquivo 100% novo.
"""

import json
import random
from pathlib import Path

from models.prompt_layer import SEGURANCA_TEXTO, SEGURANCA_IMAGEM
from services.brand_prompt_builder import carregar_brand
from utils.dimensions import get_dims, get_prompt_size_str

_FORMATOS_PATH = Path(__file__).parent.parent / "configs" / "formatos.json"
_formatos_cache: dict | None = None


def _carregar_formatos() -> dict:
    """Carrega e cacheia o JSON de formatos."""
    global _formatos_cache
    if _formatos_cache is not None:
        return _formatos_cache
    try:
        if _FORMATOS_PATH.exists():
            _formatos_cache = json.loads(_FORMATOS_PATH.read_text(encoding="utf-8"))
            return _formatos_cache
    except Exception:
        pass
    _formatos_cache = {"formatos": []}
    return _formatos_cache


class PromptComposer:
    """Compoe prompts em 4 camadas: seguranca + plataforma + marca + post."""

    # ------------------------------------------------------------------
    # Carregar formato do JSON
    # ------------------------------------------------------------------
    @staticmethod
    def _carregar_formato(formato: str) -> dict | None:
        """Retorna config do formato pelo id. Mongo primeiro, fallback JSON."""
        # Tentar Mongo primeiro
        try:
            from data.repositories.mongo.formato_repository import FormatoRepository
            fmt = FormatoRepository.buscar(formato)
            if fmt:
                return fmt
        except Exception:
            pass

        # Fallback: JSON no disco
        data = _carregar_formatos()
        for f in data.get("formatos", []):
            if f["id"] == formato:
                return f
        return None

    # ------------------------------------------------------------------
    # Metodo principal — prompt de IMAGEM
    # ------------------------------------------------------------------
    @staticmethod
    def compor_prompt_imagem(
        slide: dict,
        position: int,
        total: int,
        brand_slug: str = "",
        formato: str = "carrossel",
    ) -> str:
        """Junta as camadas e retorna prompt final para geracao de imagem.

        Fase 6: se USE_NEW_PROMPT_MODULES=1 (default), usa os 7 modulos
        composaveis do backend/prompt_modules/. Senao, cai no legado de
        4 camadas. Feature flag permite rollback rapido.
        """
        import os

        use_new = os.getenv("USE_NEW_PROMPT_MODULES", "1") == "1"
        if use_new:
            novo = PromptComposer._compor_com_modules(
                slide, position, total, brand_slug, formato
            )
            if novo and len(novo) > 200:
                # Adicionar instrucao extra se houver
                instrucao = slide.get("instrucao_extra", "")
                if instrucao:
                    novo += f"\n\nINSTRUCAO ADICIONAL DO USUARIO: {instrucao}"
                return novo
            # Se falhou, cai no legado

        # --- Legado (4 camadas) ---
        camada_seg = SEGURANCA_IMAGEM.strip()
        camada_plat = PromptComposer._camada_plataforma(formato)
        camada_marca = PromptComposer._camada_marca_imagem(brand_slug)
        camada_post = PromptComposer._camada_post_imagem(
            slide, position, total, brand_slug, formato
        )

        partes = [camada_seg, camada_plat, camada_marca, camada_post]

        # Instrucao extra (feedback do usuario)
        instrucao = slide.get("instrucao_extra", "")
        if instrucao:
            partes.append(f"INSTRUCAO ADICIONAL DO USUARIO: {instrucao}")

        prompt = "\n\n".join(p for p in partes if p)

        # Seed + timestamp para forcar variacao visual a cada geracao
        import time
        prompt += f"\n\n[variation-id:{random.randint(10000, 99999)}-{int(time.time())}] Crie uma composicao visual UNICA. Varie posicao dos elementos, angulo da ilustracao e intensidade dos efeitos."
        return prompt

    @staticmethod
    def _compor_com_modules(
        slide: dict,
        position: int,
        total: int,
        brand_slug: str,
        formato: str,
    ) -> str:
        """Fase 6: chama os 7 modulos composaveis do backend/prompt_modules/.

        Decide imagem_ativa e cta_forca baseado no tipo do slide.
        """
        try:
            from prompt_modules.composer import montar
        except Exception:
            return ""

        # Mapear formato_id do sistema pros modulos (thumb, post_unico, carrossel)
        formato_map = {
            "carrossel": "carrossel",
            "post_unico": "post_unico",
            "thumbnail_youtube": "thumb",
            "thumb": "thumb",
            "capa_reels": "post_unico",
        }
        formato_id = formato_map.get(formato, "carrossel")

        # Decidir cta_forca: CTA slide final = 'forte'; slide tipo 'cta' = 'forte';
        # anuncio com cta travado = 'forte'; capa (slide 1) sem cta = 'inativo'; resto = 'padrao'
        slide_type = (slide.get("type") or "").lower()
        cta_texto = (slide.get("cta") or "").strip()
        if cta_texto:
            cta_forca = "forte"
        elif slide_type == "cta" or (position == total and total > 1):
            cta_forca = "forte"
        elif position == 1:
            cta_forca = "inativo"
        else:
            cta_forca = "padrao"

        # Imagem sempre ativa nos formatos visuais
        imagem_ativa = True

        brand = carregar_brand(brand_slug) if brand_slug else None

        try:
            return montar(
                formato_id=formato_id,
                brand=brand,
                imagem_ativa=imagem_ativa,
                cta_forca=cta_forca,
                cta_texto=cta_texto,
            )
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # Prompt de TEXTO (conteudo / copy)
    # ------------------------------------------------------------------
    @staticmethod
    def compor_prompt_texto(brand_slug: str = "", agente: str = "") -> str:
        """Junta camada 1 (seguranca texto) + camada 3 (marca — persona, tom, hooks)."""
        camada_seg = SEGURANCA_TEXTO.strip()
        camada_marca = PromptComposer._camada_marca_texto(brand_slug)

        partes = [camada_seg, camada_marca]
        if agente:
            partes.append(f"[agente: {agente}]")

        return "\n\n".join(p for p in partes if p)

    # ------------------------------------------------------------------
    # Selecao de modelo Gemini
    # ------------------------------------------------------------------
    @staticmethod
    def selecionar_modelo(
        slide: dict,
        position: int,
        total: int,
        formato: str = "carrossel",
    ) -> str:
        """Pro para capa/codigo/CTA, Flash para content.

        Le regras do configs/formatos.json; fallback hardcoded se JSON ausente.
        """
        fmt = PromptComposer._carregar_formato(formato)
        if fmt:
            mp = fmt.get("modelo_por_posicao", {})
            pro_pos = mp.get("pro_positions", "first,last,code")
            modelo_pro = mp.get("modelo_pro", "gemini-3-pro-image-preview")
            modelo_flash = mp.get("modelo_flash", "gemini-2.5-flash-image")

            if pro_pos == "all":
                return modelo_pro

            slide_type = slide.get("type", "content")
            if "first" in pro_pos and position == 1:
                return modelo_pro
            if "last" in pro_pos and position == total:
                return modelo_pro
            if "code" in pro_pos and slide_type == "code":
                return modelo_pro
            return modelo_flash

        # Fallback hardcoded
        slide_type = slide.get("type", "content")
        if position == 1 or position == total or slide_type == "code":
            return "gemini-3-pro-image-preview"
        return "gemini-2.5-flash-image"

    # ------------------------------------------------------------------
    # Preview (debug / inspecao)
    # ------------------------------------------------------------------
    @staticmethod
    def preview(
        tipo: str = "imagem",
        brand_slug: str = "",
        formato: str = "carrossel",
        slide_type: str = "content",
        position: int = 1,
        total: int = 10,
    ) -> dict:
        """Retorna dict com cada camada separada + prompt final + total caracteres."""
        # Montar slide ficticio para preview
        slide = _slide_ficticio(slide_type)

        if tipo == "texto":
            seg = SEGURANCA_TEXTO.strip()
            marca = PromptComposer._camada_marca_texto(brand_slug)
            prompt_final = PromptComposer.compor_prompt_texto(brand_slug)
            return {
                "camada_seguranca": seg,
                "camada_marca": marca,
                "prompt_final": prompt_final,
                "total_caracteres": len(prompt_final),
            }

        seg = SEGURANCA_IMAGEM.strip()
        plat = PromptComposer._camada_plataforma(formato)
        marca = PromptComposer._camada_marca_imagem(brand_slug)
        post = PromptComposer._camada_post_imagem(
            slide, position, total, brand_slug, formato
        )
        prompt_final = PromptComposer.compor_prompt_imagem(
            slide, position, total, brand_slug, formato
        )
        modelo = PromptComposer.selecionar_modelo(slide, position, total, formato)

        return {
            "camada_seguranca": seg,
            "camada_plataforma": plat,
            "camada_marca": marca,
            "camada_post": post,
            "prompt_final": prompt_final,
            "total_caracteres": len(prompt_final),
            "modelo_selecionado": modelo,
        }

    # ==================================================================
    # CAMADAS INTERNAS
    # ==================================================================

    @staticmethod
    def _camada_plataforma(formato: str) -> str:
        """Dimensoes + layout rules do formato — le do configs/formatos.json."""
        fmt = PromptComposer._carregar_formato(formato)
        dims = get_dims(formato)
        size_str = get_prompt_size_str(formato)

        regras: list[str] = []
        regras.append(f"FORMATO: {size_str}, aspect ratio {dims['ratio']} ({dims['label']}).")

        if fmt and fmt.get("layout_rules"):
            regras.extend(fmt["layout_rules"])

        return " ".join(regras)

    @staticmethod
    def _camada_marca_imagem(brand_slug: str) -> str:
        """Cores, visual, elementos do brand profile para prompt de imagem."""
        if not brand_slug:
            return ""
        brand = carregar_brand(brand_slug)
        if not brand:
            return ""

        cores = brand.get("cores", {})
        visual = brand.get("visual", {})
        elementos = brand.get("elementos", {})

        partes: list[str] = []

        # Fundo
        estilo_fundo = visual.get("estilo_fundo", "")
        if estilo_fundo:
            partes.append(estilo_fundo)

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

        # Elemento decorativo
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
        estilo_card = visual.get("estilo_card", "")
        if estilo_card:
            partes.append(estilo_card)

        # Texto
        estilo_texto = visual.get("estilo_texto", "")
        if estilo_texto:
            partes.append(estilo_texto)

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
        regras = visual.get("regras_extras", "")
        if regras:
            partes.append(regras)

        return " ".join(p for p in partes if p)

    @staticmethod
    def _camada_marca_texto(brand_slug: str) -> str:
        """Persona, tom, linguagem, publico, hooks, anti-patterns do brand profile."""
        if not brand_slug:
            return ""
        brand = carregar_brand(brand_slug)
        if not brand:
            return ""

        com = brand.get("comunicacao", {})
        partes: list[str] = []

        partes.append(f"MARCA: {brand.get('nome', brand_slug)}")

        if com.get("persona"):
            partes.append(f"PERSONA: {com['persona']}")
        if com.get("tom"):
            partes.append(f"TOM: {com['tom']}")
        if com.get("linguagem"):
            partes.append(f"LINGUAGEM: {com['linguagem']}")
        if com.get("publico"):
            partes.append(f"PUBLICO: {com['publico']}")

        # Hooks padrao
        hooks = com.get("hooks_padrao", [])
        if hooks:
            partes.append("HOOKS PADRAO:\n" + "\n".join(f"- {h}" for h in hooks))

        # Hooks proibidos
        proibidos = com.get("hooks_proibidos", [])
        if proibidos:
            partes.append(
                "HOOKS PROIBIDOS:\n" + "\n".join(f"- {h}" for h in proibidos)
            )

        # CTA padrao
        cta = com.get("cta_padrao", [])
        if cta:
            partes.append("CTA PADRAO:\n" + "\n".join(f"- {c}" for c in cta))

        # Topicos de autoridade
        topicos = com.get("topicos_autoridade", [])
        if topicos:
            partes.append(f"TOPICOS DE AUTORIDADE: {', '.join(topicos)}")

        # Anti-patterns
        anti = com.get("anti_patterns", [])
        if anti:
            partes.append("ANTI-PATTERNS:\n" + "\n".join(f"- {a}" for a in anti))

        # Palavras proibidas
        proib = com.get("palavras_proibidas", [])
        if proib:
            partes.append(f"PALAVRAS PROIBIDAS: {', '.join(proib)}")

        # Exemplos de frase
        exemplos = com.get("exemplos_frase", [])
        if exemplos:
            partes.append(
                "EXEMPLOS DE FRASE:\n" + "\n".join(f'- "{e}"' for e in exemplos)
            )

        return "\n".join(partes)

    # ------------------------------------------------------------------
    # Camada 4 — Post (dispatch por tipo de slide)
    # ------------------------------------------------------------------
    @staticmethod
    def _camada_post_imagem(
        slide: dict,
        position: int,
        total: int,
        brand_slug: str,
        formato: str,
    ) -> str:
        """Despacha para o builder especifico do tipo de slide."""
        slide_type = slide.get("type", "content")
        dims = get_dims(formato)
        size_str = get_prompt_size_str(formato)
        ratio = dims["ratio"]

        fmt = PromptComposer._carregar_formato(formato)
        tem_rodape = fmt.get("tem_rodape", True) if fmt else (formato == "carrossel")
        counter = f"{position}/{total}" if tem_rodape else ""

        brand = carregar_brand(brand_slug) if brand_slug else None
        elementos = brand.get("elementos", {}) if brand else {}
        cores = brand.get("cores", {}) if brand else {}
        visual = brand.get("visual", {}) if brand else {}

        rodape = _rodape_instruction(elementos, counter, brand_slug) if tem_rodape else ""

        # Thumbnail YouTube — prompt especial
        if formato == "thumbnail_youtube":
            return _thumbnail(slide, cores, ratio, size_str)

        # Illustration override
        illustration = slide.get("illustration_description", "")
        if illustration:
            title = slide.get("title", slide.get("headline", ""))
            return (
                f"Crie slide LinkedIn {ratio} ({size_str}). "
                f"Titulo em destaque: '{title}'. "
                f"A MAIOR PARTE DO SLIDE deve ser ocupada por: {illustration}"
            )

        if slide_type == "cover":
            return _cover(slide, elementos, cores, visual, rodape, ratio, size_str)
        if slide_type == "cta":
            return _cta(slide, elementos, cores, visual, rodape, ratio, size_str)
        if slide_type == "code":
            return _code(slide, cores, rodape, counter, ratio, size_str)
        if slide_type == "comparison":
            return _comparison(slide, cores, rodape, counter, ratio, size_str)
        return _content(slide, elementos, cores, visual, rodape, counter, ratio, size_str)


# ======================================================================
# Funcoes internas de camada 4 (post) — fora da classe para legibilidade
# ======================================================================


def _rodape_instruction(elementos: dict, counter: str, brand_slug: str | None = None) -> str:
    """Monta instrucao do rodape."""
    nome = elementos.get("rodape_nome", "")
    return f"Rodape: apenas texto '{nome}' + '{counter}' no canto inferior."


def _cover(slide, elementos, cores, visual, rodape, ratio, size_str) -> str:
    headline = slide.get("headline", "")
    subline = slide.get("subline", "")
    cta = slide.get("cta", "")
    badge = elementos.get("badge_topo", "")
    badge_cor = elementos.get("badge_topo_cor", cores.get("acento_secundario", ""))
    desenho = visual.get("estilo_desenho", "")

    cta_clause = ""
    if cta:
        # Instrucao explicita pro Gemini renderizar o botao com texto EXATO.
        # Sem isso, o modelo aluciona um CTA generico ("Fale com o comercial" etc).
        cta_clause = (
            f"BOTAO CTA OBRIGATORIO no slide: retangulo arredondado em destaque "
            f"({cores.get('acento_principal', '#A78BFA')}) com o texto EXATO "
            f"'{cta}' centralizado em branco bold. NAO traduza, NAO altere, NAO invente "
            f"outro texto pro botao. Use literalmente '{cta}' caractere por caractere. "
        )

    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). "
        f"Badge pill ({badge_cor}) no topo: '{badge}'. "
        f"Headline ENORME em {cores.get('texto_principal', 'branco')}, "
        f"com palavras-chave em {cores.get('acento_principal', '')} bold: '{headline}'. "
        f"Subline em {cores.get('texto_secundario', 'cinza')}: '{subline}'. "
        f"{cta_clause}"
        f"Na parte inferior: {desenho} "
        f"{rodape} TODO texto LEGIVEL."
    )


def _content(slide, elementos, cores, visual, rodape, counter, ratio, size_str) -> str:
    title = slide.get("title", "")
    etapa = slide.get("etapa", "")
    bullets = slide.get("bullets", [])
    bullets_text = "\n".join(f"- {b}" for b in bullets)
    desenho = visual.get("estilo_desenho", "")

    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). "
        f"Card central GRANDE com o estilo definido pelo design system. "
        f"Badge pill {cores.get('acento_principal', '')} no topo do card: '{etapa}'. "
        f"Titulo GRANDE em {cores.get('texto_principal', 'branco')} bold: '{title}'. "
        f"Bullets em {cores.get('texto_secundario', 'cinza')}, "
        f"palavras-chave em negrito ou {cores.get('acento_principal', '')}:\n{bullets_text}\n"
        f"No fundo atras do card: {desenho} "
        f"{rodape} Texto LEGIVEL."
    )


def _code(slide, cores, rodape, counter, ratio, size_str) -> str:
    code = slide.get("code", "")
    caption = slide.get("caption", "")
    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). "
        f"Badge pill {cores.get('acento_secundario', '')} no topo: 'CODIGO REAL'. "
        f"Janela de terminal estilo macOS: barra com 3 botoes (vermelho, amarelo, verde), "
        f"corpo escuro com codigo em {cores.get('acento_secundario', 'verde')}. "
        f"CADA CARACTERE deve ser LEGIVEL. "
        f"Codigo:\n{code}\n"
        f"Caption: '{caption}'. "
        f"{rodape}"
    )


def _comparison(slide, cores, rodape, counter, ratio, size_str) -> str:
    left_label = slide.get("left_label", "")
    right_label = slide.get("right_label", "")
    left_items = slide.get("left_items", [])
    right_items = slide.get("right_items", [])
    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). "
        f"Card central com dois blocos lado a lado. "
        f"Esquerdo ({cores.get('acento_negativo', 'vermelho')}): "
        f"'{left_label}' -- {', '.join(left_items)}. "
        f"Direito ({cores.get('acento_principal', 'roxo')}): "
        f"'{right_label}' -- {', '.join(right_items)}. "
        f"{rodape}"
    )


def _cta(slide, elementos, cores, visual, rodape, ratio, size_str) -> str:
    headline = slide.get("headline", "")
    subline = slide.get("subline", "")
    cta = slide.get("cta", "")
    tags = slide.get("tags", [])
    tags_text = ", ".join(tags)
    desenho = visual.get("estilo_desenho", "")

    cta_clause = ""
    if cta:
        cta_clause = (
            f"BOTAO CTA OBRIGATORIO em destaque com texto EXATO '{cta}' "
            f"centralizado em branco bold sobre {cores.get('acento_principal', '#A78BFA')}. "
            f"NAO traduza, NAO altere, NAO invente outro texto. "
        )

    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). "
        f"Headline GRANDE em {cores.get('texto_principal', 'branco')} bold: '{headline}'. "
        f"Texto em {cores.get('texto_secundario', 'cinza')}: '{subline}'. "
        f"Tags em badges pill: {tags_text}. "
        f"{cta_clause}"
        f"{desenho} sutil no fundo. "
        f"Rodape: '{elementos.get('rodape_nome', '')} -- "
        f"{elementos.get('rodape_instituicao', '')} -- "
        f"{elementos.get('rodape_extra', '')}'. "
        f"Atmosfera premium."
    )


def _thumbnail(slide, cores, ratio, size_str) -> str:
    headline = (
        slide.get("headline", "")
        or slide.get("title", "")
        or slide.get("titulo", "")
    )
    if not headline:
        for el in slide.get("elementos", []):
            if "titulo" in el.get("tipo", ""):
                h = el.get("texto", el.get("conteudo", ""))
                if isinstance(h, list):
                    headline = " ".join(
                        x.get("texto", "") if isinstance(x, dict) else str(x)
                        for x in h
                    )
                else:
                    headline = h
                break
    if not headline:
        headline = slide.get("subline", "") or slide.get("corpo", "") or "TECH"

    principal = cores.get("acento_principal", "#A78BFA")
    fundo = cores.get("fundo", "#0A0A0F")
    return (
        f"YouTube thumbnail, {ratio} horizontal landscape ({size_str}). "
        f"RIGHT SIDE (40%) = photorealistic portrait of creator. "
        f"LEFT SIDE (60%) = HUGE bold text: '{headline}' in white with dark outline. "
        f"Background: vibrant gradient using brand colors {principal} and {fundo}. "
        f"High contrast, eye-catching, modern YouTube 2025 style. "
        f"ONLY two elements: creator's face + big text. Nothing else."
    )


def _slide_ficticio(slide_type: str) -> dict:
    """Cria slide ficticio para preview/debug."""
    if slide_type == "cover":
        return {"type": "cover", "headline": "[HEADLINE PREVIEW]", "subline": "[SUBLINE]"}
    if slide_type == "cta":
        return {
            "type": "cta",
            "headline": "[CTA HEADLINE]",
            "subline": "[CTA SUBLINE]",
            "tags": ["#tag1", "#tag2"],
        }
    if slide_type == "code":
        return {
            "type": "code",
            "code": "print('hello world')",
            "caption": "[CAPTION]",
        }
    if slide_type == "comparison":
        return {
            "type": "comparison",
            "left_label": "SEM",
            "right_label": "COM",
            "left_items": ["item1"],
            "right_items": ["item2"],
        }
    return {
        "type": "content",
        "title": "[TITULO PREVIEW]",
        "bullets": ["bullet 1", "bullet 2"],
        "etapa": "PREVIEW",
    }
