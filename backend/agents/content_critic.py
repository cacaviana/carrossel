import json
import os
from pathlib import Path

import anthropic
import openai

from utils.json_parser import parse_llm_json

PROMPT_PATH = Path(__file__).parent / "content-critic.md"
if not PROMPT_PATH.exists():
    PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "agents" / "content-critic.md"


async def executar(
    conteudo: dict,
    formato: str,
    claude_api_key: str = "",
) -> dict:
    """Executa o Content Critic: avalia conteudo final com score em 6 dimensoes.

    Retorna: dict com clarity, impact, originality, scroll_stop, cta_strength,
             final_score, decision, best_variation, feedback
    """
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""

    user_prompt = f"Conteudo final para avaliacao:\n{json.dumps(conteudo, ensure_ascii=False, indent=2)}\n"
    user_prompt += f"Formato: {formato}\n"
    user_prompt += "\nAvalie com score de 0 a 10 em cada dimensao. Responda em JSON."
    user_prompt += "\nResposta OBRIGATORIAMENTE em JSON valido. Sem comentarios, sem trailing commas."

    # Tentar Claude primeiro, fallback pra OpenAI
    try:
        client = anthropic.AsyncAnthropic(api_key=claude_api_key)
        message = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return parse_llm_json(message.content[0].text)
    except Exception as e:
        print(f"[content_critic] Claude falhou: {e}. Tentando OpenAI...")

    openai_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_key:
        raise RuntimeError("Claude sem creditos e OpenAI nao configurada")
    oai_client = openai.AsyncOpenAI(api_key=openai_key)
    response = await oai_client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2048,
        temperature=0.7,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    result = parse_llm_json(response.choices[0].message.content or "")
    result["_provider"] = "openai"
    result["_fallback"] = True
    return result
