import anthropic

from factories.conteudo_factory import build_system_prompt, build_user_prompt
from utils.json_parser import parse_llm_json


async def gerar_conteudo(
    claude_api_key: str,
    disciplina: str | None = None,
    tecnologia: str | None = None,
    tema_custom: str | None = None,
    texto_livre: str | None = None,
    total_slides: int = 10,
    tipo_carrossel: str = "texto",
) -> dict:
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(disciplina, tecnologia, tema_custom, texto_livre, total_slides, tipo_carrossel)

    client = anthropic.AsyncAnthropic(api_key=claude_api_key)
    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return parse_llm_json(message.content[0].text)
