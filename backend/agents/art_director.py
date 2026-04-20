import json
import os
from pathlib import Path

import anthropic
import openai

from utils.json_parser import parse_llm_json

PROMPT_PATH = Path(__file__).parent / "art-director.md"
if not PROMPT_PATH.exists():
    PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "agents" / "art-director.md"


def _todos_slides_viram_sem_avatar(avatar_mode: str, brand_palette: dict | None) -> bool:
    """Decide se vale pular o Art Director pra esse pipeline.

    Cenarios em que o short-circuit ajuda:
    1. avatar_mode == 'sem' — intencional: sem pessoa em nenhum slide
    2. avatar_mode != 'sem' MAS a brand nao tem REFS FISICAS no pool com_avatar
       (nome iniciando por 'ref_ca_' em brand_assets) — todos os slides caem em
       sem_avatar pelo fallback do pool.

    Importante: consulta refs FISICAS, nao o padrao_visual textual. O padrao_visual
    pode ter descricao com_avatar escrita mas nenhuma imagem real — o que gera
    descricoes com pessoa que conflitam com ref sem_avatar que o Gemini recebe.
    """
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


def _short_circuit_sem_avatar(copy: dict) -> dict:
    """Gera prompts minimos pra slides sem avatar — sem chamar Claude.

    Cada ref da marca ja eh template completo (fundo + card + logo + cores).
    Descricoes longas do Art Director so conflitavam com a composicao da ref.
    Aqui passamos APENAS o texto de cada slide; o image_generator preserva a
    composicao da ref anexada.
    """
    slides = copy.get("slides", []) if isinstance(copy, dict) else []
    prompts = []
    for i, slide in enumerate(slides, start=1):
        titulo = slide.get("titulo") or slide.get("title") or ""
        corpo = slide.get("corpo") or slide.get("body") or slide.get("subtitle") or ""

        # Minimo viavel: manda reproduzir a composicao da ref anexada, trocando so o texto.
        # Sem prescricoes de fundo, cores ou layout (tudo isso vem da ref visual).
        illustration = (
            "REPLICATE the attached reference image pixel-for-pixel as closely as possible, "
            "changing ONLY the text content. Everything else MUST match the reference:\n"
            "\n"
            "BACKGROUND: copy the EXACT background of the reference. "
            "If the reference background is PURE WHITE, the output background MUST be PURE WHITE — "
            "do NOT add gradients, color tints, textures, or decorative washes to the background.\n"
            "\n"
            "COLORS: use the EXACT RGB values from the reference. "
            "If a colored box in the reference is a washed-out near-neutral pastel (barely visible, "
            "almost gray-lavender or gray-mint), the output MUST also be washed-out near-neutral. "
            "DO NOT saturate, DO NOT enhance, DO NOT make vivid, DO NOT shift hue. "
            "A lavender box stays lavender (not purple/magenta). A mint box stays mint (not rose/lilac).\n"
            "\n"
            "COMPOSITION: preserve card positions, sizes, logo placement, arrows, footer — identical to the reference.\n"
            "\n"
            f"TEXT REPLACEMENT: replace only the text content with: titulo='{titulo}'"
            + (f", corpo='{corpo}'" if corpo else "")
            + "."
        )
        prompts.append({
            "slide_index": i,
            "prompt": titulo,
            "illustration_description": illustration,
            "pool_usado": "sem_avatar",
            "composicao_usada": "copiar_da_referencia",
        })
    return {"prompts": prompts, "_provider": "short_circuit_sem_avatar"}


async def executar(
    copy: dict,
    hook: str,
    formato: str,
    brand_palette: dict | None = None,
    visual_memory: str | None = None,
    claude_api_key: str = "",
    avatar_mode: str = "livre",
) -> dict:
    """Executa o Art Director: gera prompt de imagem detalhado por slide.

    Retorna: dict com prompts: [{slide_index, prompt}]
    """
    # SHORT-CIRCUIT: pular Claude quando todos os slides vao acabar em sem_avatar
    # (avatar_mode='sem' explicito OU brand sem refs com_avatar -> fallback pra sem).
    if _todos_slides_viram_sem_avatar(avatar_mode, brand_palette):
        return _short_circuit_sem_avatar(copy)

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""

    # Separar feedback e cena anterior se existirem
    feedback = copy.pop("_feedback", "") if isinstance(copy, dict) else ""
    cena_anterior = copy.pop("_cena_anterior", []) if isinstance(copy, dict) else []

    user_prompt = f"Copy completa:\n{json.dumps(copy, ensure_ascii=False, indent=2)}\n"
    user_prompt += f"Formato: {formato}\n"

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
    return result
