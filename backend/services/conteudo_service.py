import json
import re

import anthropic

from factories.conteudo_factory import build_system_prompt, build_user_prompt


def _parse_json(response_text: str) -> dict:
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if fence_match:
        return json.loads(fence_match.group(1))
    start = response_text.find("{")
    end = response_text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("Claude não retornou JSON válido")
    return json.loads(response_text[start:end])


async def gerar_conteudo(
    claude_api_key: str,
    disciplina: str | None = None,
    tecnologia: str | None = None,
    tema_custom: str | None = None,
    texto_livre: str | None = None,
    total_slides: int = 10,
) -> dict:
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(disciplina, tecnologia, tema_custom, texto_livre, total_slides)

    client = anthropic.AsyncAnthropic(api_key=claude_api_key)
    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return _parse_json(message.content[0].text)
