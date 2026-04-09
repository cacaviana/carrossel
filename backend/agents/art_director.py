import json
import os
from pathlib import Path

import anthropic
import openai

from utils.json_parser import parse_llm_json

PROMPT_PATH = Path(__file__).parent / "art-director.md"
if not PROMPT_PATH.exists():
    PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "agents" / "art-director.md"


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

    if brand_palette and has_references:
        # === MODO REFERENCIA: Art Director foca em DIRECAO DE CENA ===
        nome = brand_palette.get("nome", "")
        com = brand_palette.get("comunicacao", {})

        user_prompt += (
            f"\n=== MARCA: {nome} ===\n"
            f"TOM: {com.get('tom', '')}\n"
            f"PUBLICO: {com.get('publico', '')}\n\n"
            f"=== INSTRUCAO ESPECIAL ===\n"
            f"Esta marca tem IMAGENS DE REFERENCIA que definem o estilo visual (cores, fontes, doodles).\n"
            f"Voce NAO precisa descrever estilo visual nos prompts. A imagem de referencia faz isso.\n\n"
            f"Seu papel e de DIRETOR DE CENA. Para cada slide, descreva:\n"
            f"- Que CENA a pessoa/objeto esta (ex: 'sentada no sofa lendo um livro', 'em pe segurando cafe')\n"
            f"- Que OBJETOS/ELEMENTOS aparecem (ex: 'xicara fumegante, livros empilhados, planta')\n"
            f"- Que ACAO esta acontecendo (ex: 'sorrindo pra camera', 'escrevendo num caderno')\n"
            f"- Que MOOD o slide tem (ex: 'aconchegante manha de domingo', 'energia de segunda-feira')\n\n"
            f"NAO descreva cores, fontes, gradientes, doodles — isso vem da referencia.\n"
            f"Foque em: cena, pose, objetos, acao, mood.\n"
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

    # Avatar: pedir illustration_description com cena de pessoa
    needs_scene = avatar_mode in ("sim", "capa")

    if has_references or needs_scene:
        scene_instruction = (
            "\nPara cada slide, gere:"
            "\n- 'prompt': o texto do slide (titulo + subtitulo)"
            "\n- 'illustration_description': descricao DETALHADA da cena (MINIMO 80 palavras)"
            "\n"
            "\nA illustration_description deve descrever a CENA COMPLETA como um diretor de cinema:"
            "\n  - PESSOA: o que esta fazendo, pose, expressao, roupa, objeto na mao"
            "\n  - CENARIO: onde esta (sofa, mesa, cozinha, parque), iluminacao"
            "\n  - OBJETOS: o que aparece ao redor (cafe, livros, plantas, notebook)"
            "\n  - MOOD: que sentimento transmite"
            "\n"
            "\nIMPORTANTE: A pessoa DEVE parecer REAL e FOTOGRAFICA. Descreva como se fosse uma "
            "FOTO PROFISSIONAL de uma pessoa real, NAO um desenho, NAO uma ilustracao, NAO um cartoon."
            "\n"
            "\nEXEMPLOS de boa illustration_description:"
            "\n  'Young man standing confidently in front of a desk with a laptop and code on screen, arms crossed, wearing a dark hoodie. Behind him, a dark modern office with subtle purple neon lighting. Sharp, professional photography style. Focused, determined energy.'"
            "\n  'Woman standing at a clean white desk, writing in a journal with a pink pen. A laptop is open beside her. Small vase with dried flowers. Natural daylight. Focused but relaxed energy, productive morning vibes. Photorealistic style.'"
            "\n"
        )
        if has_references:
            scene_instruction += "\nNAO descreva estilo visual (cores, fontes, doodles) — so a cena.\n"

        scene_instruction += (
            "\nResponda em JSON: {\"prompts\": [{\"slide_index\": 1, \"prompt\": \"titulo do slide\", \"illustration_description\": \"descricao detalhada da cena com minimo 80 palavras\"}]}"
            "\nResposta OBRIGATORIAMENTE em JSON valido."
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
