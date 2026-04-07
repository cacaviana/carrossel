from pathlib import Path

import anthropic

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
