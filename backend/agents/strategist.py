import os
from pathlib import Path

import anthropic
import openai

from utils.json_parser import parse_llm_json

PROMPT_PATH = Path(__file__).parent / "strategist.md"
if not PROMPT_PATH.exists():
    PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "agents" / "strategist.md"


async def executar(
    tema: str,
    formato: str,
    modo_funil: bool,
    tendencias: list[dict] | None = None,
    feedback: str = "",
    claude_api_key: str = "",
) -> dict:
    """Executa o Strategist: gera briefing estruturado.

    Retorna: dict com briefing, funil, etc.
    """
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""

    user_prompt = (
        f"TEMA OBRIGATORIO (nao mude, nao substitua, nao invente outro): {tema}\n"
        f"Formato: {formato}\n"
        f"REGRA CRITICA: O briefing DEVE ser sobre o tema acima. "
        f"Use EXATAMENTE esse assunto como tema_principal. "
        f"NAO gere conteudo sobre outro assunto.\n"
    )
    if modo_funil:
        user_prompt += "Modo funil ativo: gere 5-7 pecas conectadas (topo/meio/fundo).\n"
    if tendencias:
        user_prompt += "\nTendencias atuais:\n"
        for t in tendencias[:5]:
            user_prompt += f"- {t['titulo']} ({t['fonte']})\n"
    if feedback:
        user_prompt += f"\nFEEDBACK DO USUARIO (versao anterior rejeitada): {feedback}\n"
        user_prompt += "GERE um briefing COMPLETAMENTE DIFERENTE, seguindo o feedback acima.\n"
    user_prompt += "\nResposta OBRIGATORIAMENTE em JSON valido. Sem comentarios, sem trailing commas."

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
        if "raw_text" in result:
            return {"briefing": result["raw_text"], "raw": True}
        return result
    except Exception as e:
        print(f"[strategist] Claude falhou: {e}. Tentando OpenAI...")

    openai_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_key:
        raise RuntimeError("Claude sem creditos e OpenAI nao configurada")
    oai_client = openai.AsyncOpenAI(api_key=openai_key)
    response = await oai_client.chat.completions.create(
        model="gpt-4o",
        max_tokens=4096,
        temperature=0.9,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    result = parse_llm_json(response.choices[0].message.content or "")
    result["_provider"] = "openai"
    result["_fallback"] = True
    if "raw_text" in result:
        return {"briefing": result["raw_text"], "raw": True}
    return result
