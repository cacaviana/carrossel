import json
from pathlib import Path

import anthropic

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
) -> dict:
    """Executa o Art Director: gera prompt de imagem detalhado por slide.

    Retorna: dict com prompts: [{slide_index, prompt}]
    """
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""

    user_prompt = f"Copy completa:\n{json.dumps(copy, ensure_ascii=False, indent=2)}\n"
    user_prompt += f"Hook selecionado: {hook}\n"
    user_prompt += f"Formato: {formato}\n"
    if brand_palette:
        # Extrair visual da marca pra guiar o art director
        visual = brand_palette.get("visual", {})
        cores = brand_palette.get("cores", {})
        nome = brand_palette.get("nome", "")
        com = brand_palette.get("comunicacao", {})

        user_prompt += (
            f"\n=== IDENTIDADE VISUAL DA MARCA '{nome}' (OBRIGATORIO — SUBSTITUI O PADRAO IT VALLEY) ===\n"
            f"CORES: fundo={cores.get('fundo','')}, principal={cores.get('acento_principal','')}, "
            f"secundario={cores.get('acento_secundario','')}, texto={cores.get('texto_principal','')}, "
            f"texto_sec={cores.get('texto_secundario','')}\n"
            f"FUNDO: {visual.get('estilo_fundo', '')}\n"
            f"DESENHO/ILUSTRACAO: {visual.get('estilo_desenho', '')}\n"
            f"CARDS: {visual.get('estilo_card', '')}\n"
            f"TEXTOS: {visual.get('estilo_texto', '')}\n"
            f"REGRAS: {visual.get('regras_extras', '')}\n"
            f"TOM: {com.get('tom', '')}\n"
            f"IMPORTANTE: Use EXATAMENTE estas cores e estilos nos prompts de imagem. "
            f"NAO use dark mode roxo se a marca nao for dark. "
            f"NAO use cores de outra marca. Use EXATAMENTE as cores descritas acima.\n"
            f"=== FIM IDENTIDADE VISUAL ===\n"
        )
    if visual_memory:
        user_prompt += f"\nPreferencias visuais do usuario:\n{visual_memory}\n"
    user_prompt += "\nGere prompts de imagem detalhados para cada slide, usando as cores e estilo da marca. Responda em JSON com array 'prompts'."
    user_prompt += "\nResposta OBRIGATORIAMENTE em JSON valido. Sem comentarios, sem trailing commas."

    client = anthropic.AsyncAnthropic(api_key=claude_api_key)
    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return parse_llm_json(message.content[0].text)
