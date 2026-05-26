import json
import os
from pathlib import Path

import anthropic
import openai

from utils.json_parser import parse_llm_json

PROMPT_PATH = Path(__file__).parent / "art-director.md"
if not PROMPT_PATH.exists():
    PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "agents" / "art-director.md"


def _carregar_dna_agregado(brand_palette: dict | None) -> dict | None:
    """Busca o dna_agregado da brand no Mongo (gerado por dna_aggregator_service).
    Retorna None se nao tiver — fluxo cai pro DNA antigo como fallback."""
    if not brand_palette:
        return None
    # Se ja veio no brand_palette dict, usar direto
    if "dna_agregado" in brand_palette:
        return brand_palette.get("dna_agregado")
    brand_slug = brand_palette.get("slug")
    if not brand_slug:
        return None
    try:
        from data.connections.mongo_connection import get_mongo_db
        db = get_mongo_db()
        if db is None:
            return None
        doc = db.brands.find_one({"slug": brand_slug}, {"dna_agregado": 1})
        return (doc or {}).get("dna_agregado")
    except Exception as e:
        print(f"[art_director] erro ao carregar dna_agregado: {e}")
        return None


def _todos_slides_viram_sem_avatar(avatar_mode: str, brand_palette: dict | None, formato: str | None = None) -> bool:
    """Decide se vale pular o Art Director pra esse pipeline.

    Cenarios em que o short-circuit ajuda:
    1. avatar_mode == 'sem' — intencional: sem pessoa em nenhum slide
    2. avatar_mode != 'sem' MAS a brand nao tem REFS FISICAS no pool com_avatar
       (nome iniciando por 'ref_ca_' em brand_assets) — todos os slides caem em
       sem_avatar pelo fallback do pool.

    EXCECAO: formato 'thumbnail_youtube' sempre requer avatar (RN-005) — nunca
    short-circuit. Mesmo que a brand nao tenha ref com_avatar cadastrada, o
    art_director precisa rodar pra dirigir a cena com o avatar disponivel
    (senao Gemini inventa cenario aleatorio, tipo naves ET).

    Importante: consulta refs FISICAS, nao o padrao_visual textual.
    """
    if formato == "thumbnail_youtube":
        return False
    if avatar_mode == "sem":
        return True
    if not brand_palette:
        return False
    brand_slug = brand_palette.get("slug")
    if not brand_slug:
        return False
    try:
        from factories.imagem_factory import _load_ref_docs_by_pool
        docs_com = _load_ref_docs_by_pool(brand_slug, "com_avatar")
    except Exception:
        return False  # em duvida, mantem fluxo normal
    return not docs_com


async def _short_circuit_sem_avatar(
    copy: dict,
    brand_palette: dict | None = None,
    pipeline_id: str | None = None,
    claude_api_key: str = "",
) -> dict:
    """Gera prompts pra slides sem avatar usando a ANALISE VISUAL pre-computada da ref.

    Fluxo:
    1. Sorteia qual ref sera usada (determinismo por pipeline_id)
    2. Busca analise_visual da ref no Mongo (cache). Se nao tem, chama Claude Vision uma vez.
    3. Usa a analise (composicao + paleta + blocos_conteudo) pra gerar illustration
       adaptada ao copy — evita caixas vazias quando ref tem 3 blocos mas copy tem 1.

    Fallback: se nao consegue analise (sem pipeline_id, brand sem slug, Mongo down),
    usa illustration minima generica (apenas "replique a ref anexada").
    """
    slides = copy.get("slides", []) if isinstance(copy, dict) else []
    ref_analise = await _obter_analise_ref(brand_palette, pipeline_id, claude_api_key)

    prompts = []
    for i, slide in enumerate(slides, start=1):
        titulo = slide.get("titulo") or slide.get("title") or ""
        corpo = slide.get("corpo") or slide.get("body") or slide.get("subtitle") or ""

        illustration = _build_illustration_com_analise(titulo, corpo, ref_analise)
        prompts.append({
            "slide_index": i,
            "prompt": titulo,
            "illustration_description": illustration,
            "pool_usado": "sem_avatar",
            "composicao_usada": "copiar_da_referencia",
        })
    return {"prompts": prompts, "_provider": "short_circuit_sem_avatar"}


async def _obter_analise_ref(
    brand_palette: dict | None,
    pipeline_id: str | None,
    claude_api_key: str,
) -> dict | None:
    """Descobre qual ref sera usada e retorna sua analise_visual (com cache)."""
    if not brand_palette or not pipeline_id:
        return None
    brand_slug = brand_palette.get("slug")
    if not brand_slug:
        return None
    try:
        from factories.refs_selector import escolher_refs_fixas, nome_ref_escolhida
        from services.ref_analyzer_service import obter_ou_analisar

        refs_fixas = escolher_refs_fixas(brand_slug, pipeline_id)
        ref_nome = nome_ref_escolhida(refs_fixas, "sem_avatar")
        if not ref_nome:
            return None
        return await obter_ou_analisar(brand_slug, ref_nome, claude_api_key)
    except Exception as e:
        print(f"[short_circuit] falha ao obter analise da ref: {e}")
        return None


def _build_illustration_com_analise(
    titulo: str,
    corpo: str,
    analise: dict | None,
) -> str:
    """Monta illustration_description usando a analise pre-computada da ref.

    Sem analise -> instrucao generica (mesma do caminho anterior).
    Com analise -> adapta ao copy: se copy tem 1 texto mas ref tem 3 blocos,
    manda usar apenas 1 bloco (evita caixas vazias).
    """
    partes_texto = []
    if titulo:
        partes_texto.append(f"titulo='{titulo}'")
    if corpo:
        partes_texto.append(f"corpo='{corpo}'")
    texto_str = ", ".join(partes_texto) if partes_texto else "(sem texto)"
    blocos_copy = sum(1 for x in (titulo, corpo) if x)

    # Sem analise: versao anterior (generica, pede pra replicar ref literal)
    if not analise:
        return (
            "REPLICATE the attached reference image pixel-for-pixel as closely as possible, "
            "changing ONLY the text content. Everything else MUST match the reference:\n\n"
            "BACKGROUND: copy the EXACT background. If reference is PURE WHITE, output MUST be PURE WHITE — "
            "no gradients, tints, textures.\n\n"
            "COLORS: use EXACT RGB values from reference. If washed-out pastel, stay washed-out. "
            "DO NOT saturate, DO NOT shift hue. Lavender stays lavender (not purple). Mint stays mint (not rose).\n\n"
            "COMPOSITION: preserve card positions, logo, arrows, footer — identical.\n\n"
            f"TEXT REPLACEMENT: {texto_str}."
        )

    composicao = analise.get("composicao") or ""
    paleta = analise.get("paleta") or {}
    blocos_ref = analise.get("blocos_conteudo") or 1
    tom = analise.get("tom_cores") or "neutro_pastel"

    # Paleta formatada
    paleta_parts = []
    for k, v in paleta.items():
        if v and v != "null":
            paleta_parts.append(f"{k}={v}")
    paleta_str = "; ".join(paleta_parts) if paleta_parts else "(use cores exatas da ref)"

    # Regra de adaptacao quantidade de blocos
    adaptacao = ""
    if blocos_copy < blocos_ref:
        adaptacao = (
            f"\nADAPTACAO DE BLOCOS: a referencia tem {blocos_ref} blocos de conteudo mas este slide "
            f"so tem {blocos_copy} bloco(s). Use APENAS {blocos_copy} bloco(s) centralizado(s). "
            f"NAO adicione caixas vazias ou placeholders."
        )
    elif blocos_copy > blocos_ref:
        adaptacao = (
            f"\nADAPTACAO DE BLOCOS: a referencia tem {blocos_ref} blocos mas este slide tem {blocos_copy}. "
            f"Expanda a estrutura mantendo o estilo visual."
        )

    return (
        f"Reproduzir fielmente a composicao da imagem de referencia anexada, "
        f"trocando APENAS o texto.\n\n"
        f"COMPOSICAO DA REFERENCIA (use como template):\n{composicao}\n\n"
        f"PALETA EXATA (use esses HEX, nao mude, nao saturar, nao mudar matiz):\n{paleta_str}\n\n"
        f"TOM CROMATICO: {tom}. "
        f"Se '{tom}' = 'neutro_pastel', as cores das caixas sao quase neutras (barely visible). "
        f"NAO transforme em cores vivas/vibrantes."
        f"{adaptacao}\n\n"
        f"TEXTO A USAR: {texto_str}.\n\n"
        f"REGRAS:\n"
        f"- Fundo EXATAMENTE como descrito na paleta (se fundo=#FFFFFF, manter branco puro sem gradiente)\n"
        f"- Posicao de cards, logo e elementos: identica a ref\n"
        f"- Fontes: preservar peso e estilo da ref"
    )


async def executar(
    copy: dict,
    hook: str,
    formato: str,
    brand_palette: dict | None = None,
    visual_memory: str | None = None,
    claude_api_key: str = "",
    avatar_mode: str = "livre",
    pipeline_id: str | None = None,
) -> dict:
    """Executa o Art Director: gera prompt de imagem detalhado por slide.

    Retorna: dict com prompts: [{slide_index, prompt}]
    """
    # KILL-SWITCH (DEV/TEST): ART_DIRECTOR_DISABLED=1 pula completamente o Claude/OpenAI
    # e usa o short-circuit minimalista (so manda "reproduza a ref + use este texto").
    # Util pra isolar se o problema esta no art_director ou no image_generator/Gemini.
    if os.getenv("ART_DIRECTOR_DISABLED", "0") == "1":
        return await _short_circuit_sem_avatar(
            copy, brand_palette=brand_palette,
            pipeline_id=pipeline_id, claude_api_key=claude_api_key,
        )

    # SHORT-CIRCUIT: pular Claude (modo texto) quando todos os slides vao acabar em sem_avatar
    # (avatar_mode='sem' explicito OU brand sem refs com_avatar -> fallback pra sem).
    # EXCECAO: thumbnail_youtube sempre precisa de avatar (RN-005), nunca short-circuit.
    if _todos_slides_viram_sem_avatar(avatar_mode, brand_palette, formato=formato):
        return await _short_circuit_sem_avatar(
            copy, brand_palette=brand_palette,
            pipeline_id=pipeline_id, claude_api_key=claude_api_key,
        )

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""

    # Separar feedback e cena anterior se existirem
    feedback = copy.pop("_feedback", "") if isinstance(copy, dict) else ""
    cena_anterior = copy.pop("_cena_anterior", []) if isinstance(copy, dict) else []

    user_prompt = f"Copy completa:\n{json.dumps(copy, ensure_ascii=False, indent=2)}\n"
    user_prompt += f"Formato: {formato}\n"

    # === DNA AGREGADO da brand (extraido das refs reais via dna_aggregator) ===
    # Substitui o DNA antigo (que podia estar sujo/alucinado) com analise verdadeira
    # cruzando todas as refs. Define o que e CONSTANTE (identidade) vs LIVRE (variacoes).
    dna_agregado = _carregar_dna_agregado(brand_palette)
    if dna_agregado:
        constantes = dna_agregado.get("constantes") or {}
        variaveis = dna_agregado.get("variaveis_livres") or {}
        n_refs = dna_agregado.get("n_refs_analisadas", 0)
        user_prompt += (
            f"\n=== DNA AGREGADO DA MARCA (extraido de {n_refs} refs reais) ===\n"
            f"CONSTANTES (identidade — manter SEMPRE):\n"
            f"  - paleta principal: {', '.join(constantes.get('paleta', []))}\n"
            f"  - tipografia: {constantes.get('tipografia', '')}\n"
            f"  - tom_cores: {constantes.get('tom_cores', '')}\n"
            f"  - elementos recorrentes: {', '.join(constantes.get('elementos_recorrentes', []))}\n"
            f"  - estilo geral: {constantes.get('estilo_geral', '')}\n"
            f"VARIAVEIS LIVRES (espaco criativo — pode variar):\n"
            f"  - fundos exemplos: {'; '.join(variaveis.get('fundo', [])[:3])}\n"
            f"  - composicoes: {'; '.join(variaveis.get('composicao', [])[:3])}\n"
            f"REGRA: SIGA RIGOROSAMENTE as constantes. Para fundo/composicao, use as "
            f"variaveis como inspiracao mas adapte ao tema do post atual. "
            f"NAO inclua elementos que nao estao listados (ex: nao adicionar astronauta "
            f"se nao esta nos elementos recorrentes).\n"
            f"=== FIM DNA AGREGADO ===\n"
        )


    # Se tem feedback de rejeição, PRESERVAR cena e só ajustar o que o usuario pediu
    if feedback and cena_anterior:
        user_prompt += (
            f"\n=== FEEDBACK DO USUARIO (AJUSTE MINIMO) ===\n"
            f"A cena anterior era:\n{json.dumps(cena_anterior, ensure_ascii=False, indent=2)}\n\n"
            f"O usuario pediu esta mudanca: {feedback}\n\n"
            f"INSTRUCAO: Mantenha a cena anterior EXATAMENTE como estava. "
            f"APENAS aplique o ajuste que o usuario pediu. "
            f"NAO mude o resto. NAO crie cena nova do zero.\n"
            f"=== FIM FEEDBACK ===\n"
        )

    has_references = brand_palette and brand_palette.get("prompt_referencia")

    # padrao_visual pode ter dois formatos:
    # - novo: {com_avatar: {...}, sem_avatar: {...}} — um bloco por pool
    # - legado: {tipo_foto, composicoes, ...} — um bloco unico pra todos slides
    padrao_raw = (brand_palette or {}).get("padrao_visual") or {}
    if isinstance(padrao_raw, dict) and ("com_avatar" in padrao_raw or "sem_avatar" in padrao_raw):
        padrao_com_avatar = padrao_raw.get("com_avatar") or {}
        padrao_sem_avatar = padrao_raw.get("sem_avatar") or {}
    else:
        # Legado: mesmo padrao serve pros dois pools
        padrao_com_avatar = padrao_raw if padrao_raw else {}
        padrao_sem_avatar = padrao_raw if padrao_raw else {}

    def _bloco_padrao(label: str, padrao: dict) -> str:
        if not padrao:
            return f"  {label}: (sem refs nesse pool — fallback pro outro pool)\n"
        composicoes = padrao.get("composicoes") or []
        comp_str = "\n".join(f"    - {c}" for c in composicoes) if composicoes else "    - (sem composicoes capturadas)"
        return (
            f"  {label}:\n"
            f"    tipo_foto: {padrao.get('tipo_foto', '')}\n"
            f"    iluminacao: {padrao.get('iluminacao', '')}\n"
            f"    mood: {padrao.get('mood', '')}\n"
            f"    fundo_cenario: {padrao.get('fundo_cenario', '')}\n"
            f"    relacao_pessoa_fundo: {padrao.get('relacao_pessoa_fundo', '')}\n"
            f"    elementos_overlay: {padrao.get('elementos_overlay', '')}\n"
            f"    composicoes recorrentes (escolha UMA por slide):\n{comp_str}\n"
        )

    if brand_palette and has_references:
        # === MODO REFERENCIA: Art Director foca em DIRECAO DE CENA ===
        nome = brand_palette.get("nome", "")
        com = brand_palette.get("comunicacao", {})

        user_prompt += (
            f"\n=== MARCA: {nome} ===\n"
            f"TOM: {com.get('tom', '')}\n"
            f"PUBLICO: {com.get('publico', '')}\n"
        )

        # Bloco PADRAO VISUAL — um por pool. Art director escolhe qual usar por slide.
        if padrao_com_avatar or padrao_sem_avatar:
            user_prompt += (
                f"\n=== PADRAO VISUAL DA MARCA (extraido das refs) ===\n"
                f"Dois padroes distintos — use um ou outro dependendo se o slide tem pessoa ou nao:\n"
                + _bloco_padrao("COM_AVATAR (use quando o slide TEM pessoa)", padrao_com_avatar)
                + _bloco_padrao("SEM_AVATAR (use quando o slide NAO tem pessoa — foto de fundo/objetos/texto)", padrao_sem_avatar)
                + f"=== FIM PADRAO VISUAL ===\n"
            )

        user_prompt += (
            f"\n=== INSTRUCAO ESPECIAL ===\n"
            f"Esta marca tem IMAGENS DE REFERENCIA que definem o estilo visual (cores, fontes, doodles).\n"
            f"Voce NAO precisa descrever estilo visual nos prompts. A imagem de referencia faz isso.\n\n"
            f"Seu papel e de DIRETOR DE CENA. Para cada slide, escolha o pool CORRETO (com_avatar ou sem_avatar) baseado nas regras abaixo, e pegue UMA das composicoes recorrentes desse pool.\n"
            f"- Qual COMPOSICAO usar (cite literal do pool escolhido)\n"
            f"- Que ACAO/POSE a pessoa faz (se tiver pessoa) ou qual OBJETO/CENARIO aparece\n"
            f"- Que OBJETOS aparecem ao redor coerentes com o tema\n"
            f"- Que MOOD especifico desse slide (alinhado com o mood do pool)\n\n"
            f"NAO descreva cores, fontes, gradientes, doodles — isso vem da referencia.\n"
            f"Respeite o TIPO DE FOTO do pool escolhido.\n"
            f"Foque em: composicao, pose/acao, objetos, mood.\n"
        )

    elif brand_palette:
        # === MODO PROMPT: Art Director descreve tudo (sem referencia) ===
        visual = brand_palette.get("visual") or {}
        cores = brand_palette.get("cores") or {}
        nome = brand_palette.get("nome") or ""
        com = brand_palette.get("comunicacao") or {}
        fontes = brand_palette.get("fontes") or {}

        user_prompt += (
            f"\n=== IDENTIDADE VISUAL DA MARCA '{nome}' ===\n"
            f"CORES: fundo={cores.get('fundo','')}, principal={cores.get('acento_principal','')}, "
            f"secundario={cores.get('acento_secundario','')}, texto={cores.get('texto_principal','')}\n"
            f"FONTES: titulo={fontes.get('titulo','')}, corpo={fontes.get('corpo','')}\n"
            f"FUNDO: {visual.get('estilo_fundo', '')}\n"
            f"DESENHO: {visual.get('estilo_desenho', '')}\n"
            f"CARDS: {visual.get('estilo_card', '')}\n"
            f"TEXTOS: {visual.get('estilo_texto', '')}\n"
            f"REGRAS: {visual.get('regras_extras', '')}\n"
            f"TOM: {com.get('tom', '')}\n"
            f"\nUse EXATAMENTE estas cores e estilos nos prompts.\n"
        )

    if visual_memory:
        user_prompt += f"\nPreferencias visuais do usuario:\n{visual_memory}\n"

    # Fase 6 fix: avatar_mode diz quais slides podem ter pessoa.
    # - "sem": nenhum slide tem pessoa
    # - "capa": so slide 1 (capa)
    # - "livre": capa (slide 1) + CTA (slide final)
    # - "sim": todos os slides
    # Instruir o Art Director por slide especifico.
    slides_lista = copy.get("slides", []) if isinstance(copy, dict) else []
    total_slides = len(slides_lista)

    def _slide_tem_pessoa(idx_1based: int) -> bool:
        if avatar_mode == "sem":
            return False
        if avatar_mode == "sim":
            return True
        if avatar_mode == "capa":
            return idx_1based == 1
        # livre
        return idx_1based == 1 or idx_1based == total_slides

    regras_por_slide = []
    for i, _ in enumerate(slides_lista, start=1):
        tem = _slide_tem_pessoa(i)
        regras_por_slide.append(f"  slide {i}: {'COM pessoa' if tem else 'SEM pessoa (objetos, cenario, sem gente)'}")
    if regras_por_slide:
        user_prompt += (
            "\n=== REGRAS DE PESSOA POR SLIDE (OBRIGATORIAS) ===\n"
            f"avatar_mode='{avatar_mode}' — use EXATAMENTE:\n"
            + "\n".join(regras_por_slide)
            + "\nNAO descreva pessoa em slides marcados SEM pessoa. Foco em objetos, cenario, texturas.\n"
            "=== FIM REGRAS ===\n"
        )

    needs_scene = avatar_mode in ("sim", "capa", "livre")

    if has_references or needs_scene:
        # Tipo de foto e iluminacao — fallback pro com_avatar, depois sem_avatar
        tipo_foto = (padrao_com_avatar.get("tipo_foto") or padrao_sem_avatar.get("tipo_foto") or "")
        iluminacao_ref = (padrao_com_avatar.get("iluminacao") or padrao_sem_avatar.get("iluminacao") or "")

        scene_instruction = (
            "\nPara cada slide, gere:"
            "\n- 'prompt': o texto do slide (titulo + subtitulo)"
            "\n- 'illustration_description': descricao DETALHADA da cena (MINIMO 80 palavras)"
            "\n- 'pool_usado': 'com_avatar' ou 'sem_avatar' — qual pool voce usou pra esse slide"
            "\n- 'composicao_usada': qual composicao do pool escolhido voce usou (cite literal do array)"
            "\n"
            "\n=== ESTRUTURA OBRIGATORIA POR TIPO DE SLIDE ==="
            "\nO tipo do slide (capa/conteudo/codigo/cta) determina a ESTRUTURA VISUAL, "
            "independente de qual composicao do pool voce escolher. Siga ESTRITAMENTE:"
            "\n"
            "\n- CAPA (slide 1): foco em IMPACTO — titulo grande dominante + pessoa (se pool com_avatar) "
            "ou elemento visual central forte (se sem_avatar). UM UNICO foco. NAO divide em cards."
            "\n"
            "\n- CONTEUDO: texto informativo em destaque com apoio visual. Pode ter UM elemento grafico "
            "ilustrativo (nao multiplos cards comparativos, A MENOS QUE o texto tenha claramente 2 lados "
            "opostos — ex: 'errado x certo'). Se o texto e unico (sem oposicao explicita), UM foco central."
            "\n"
            "\n- CODIGO: bloco de codigo destacado (como janela de IDE) ocupando area principal, "
            "com titulo curto acima. NUNCA divide em cards."
            "\n"
            "\n- CTA: estrutura de CHAMADA UNICA — um elemento focal central (botao, seta, icone grande, "
            "avatar apontando, convite visual). NUNCA comparacao, NUNCA 2 cards, NUNCA lista de opcoes. "
            "Um unico direcionamento que convida acao. Exemplo: 'pessoa apontando pra camera com sorriso, "
            "texto do CTA em overlay grande', ou 'botao luminoso central com icone de seta e titulo curto'."
            "\n=== FIM ESTRUTURA POR TIPO ==="
            "\n"
            "\nA illustration_description deve descrever a CENA COMPLETA como um diretor de cinema:"
            "\n  - COMPOSICAO: qual layout escolheu (das composicoes recorrentes da marca)"
            "\n  - ESTRUTURA DO TIPO: respeite a estrutura obrigatoria acima pro tipo do slide"
            "\n  - PESSOA (se tiver): pose, expressao, roupa, objeto na mao"
            "\n  - CENARIO: ambiente coerente com o fundo_cenario da marca, iluminacao coerente"
            "\n  - OBJETOS: o que aparece ao redor coerente com o tema do slide (SEM multiplicar em cards)"
            "\n  - MOOD: que sentimento transmite"
            "\n"
        )

        # A instrucao de estilo visual vem do padrao_visual da marca.
        # Removido o hardcode "FOTO PROFISSIONAL REALISTA" — marcas diferentes tem
        # tipos de foto diferentes (editorial feminina, tech com neon, lifestyle natural).
        if tipo_foto:
            scene_instruction += (
                f"\nIMPORTANTE: Esta marca usa {tipo_foto}. "
                f"Respeite esse tipo de foto exatamente — cena, iluminacao e mood devem casar com a identidade da marca."
                f"\nIluminacao tipica: {iluminacao_ref or 'natural'}.\n"
            )
        else:
            scene_instruction += (
                "\nIMPORTANTE: A pessoa/cena deve parecer uma FOTO real e coerente com o estilo da marca "
                "(se a marca tem refs, use o estilo das refs; nao force cena generica).\n"
            )

        scene_instruction += (
            "\nResponda em JSON com ESTE schema exato — nao adicione nem remova campos:"
            "\n{\"prompts\": [{"
            "\n  \"slide_index\": 1,"
            "\n  \"prompt\": \"titulo do slide\","
            "\n  \"illustration_description\": \"descricao detalhada com minimo 80 palavras\","
            "\n  \"pool_usado\": \"com_avatar ou sem_avatar\","
            "\n  \"composicao_usada\": \"cite literal uma das composicoes do pool escolhido\""
            "\n}]}"
            "\nResposta OBRIGATORIAMENTE em JSON valido com TODOS os 5 campos em cada slide."
        )
        user_prompt += scene_instruction
    else:
        user_prompt += (
            "\nGere prompts de imagem detalhados para cada slide. Responda em JSON com array 'prompts'."
            "\nResposta OBRIGATORIAMENTE em JSON valido. Sem comentarios, sem trailing commas."
        )

    # Tentar Claude primeiro, fallback pra OpenAI
    try:
        client = anthropic.AsyncAnthropic(api_key=claude_api_key)
        message = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        result = parse_llm_json(message.content[0].text)
        result["_provider"] = "anthropic"
        return result
    except Exception as e:
        print(f"[art_director] Claude falhou: {e}. Tentando OpenAI...")

    # Fallback OpenAI
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_key:
        raise RuntimeError("Claude sem creditos e OpenAI nao configurada")
    client = openai.AsyncOpenAI(api_key=openai_key)
    response = await client.chat.completions.create(
        model="gpt-4o",
        max_tokens=4096,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    result = parse_llm_json(response.choices[0].message.content or "")
    result["_provider"] = "openai"
    result["_fallback"] = True
    # Detectar recusa do moderador OpenAI (filtro de seguranca devolve raw_text sem JSON).
    # Devolver estrutura valida pra UI nao quebrar e o pipeline poder seguir mesmo assim.
    raw = (result.get("raw_text") or "").lower()
    if not result.get("prompts") and ("can't assist" in raw or "cannot assist" in raw or "sorry" in raw):
        print(f"[art_director] OpenAI recusou (filtro). Devolvendo prompts vazios.")
        result["prompts"] = []
        result["_filtro_recusou"] = True
    return result
