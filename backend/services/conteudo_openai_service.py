import json
import re

import openai

from factories.conteudo_factory import build_system_prompt, build_user_prompt


def _parse_json(response_text: str) -> dict:
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if fence_match:
        return json.loads(fence_match.group(1))
    start = response_text.find("{")
    end = response_text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("OpenAI não retornou JSON válido")
    return json.loads(response_text[start:end])


async def gerar_conteudo_openai(
    openai_api_key: str,
    disciplina: str | None = None,
    tecnologia: str | None = None,
    tema_custom: str | None = None,
    texto_livre: str | None = None,
    total_slides: int = 10,
) -> dict:
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(disciplina, tecnologia, tema_custom, texto_livre, total_slides)

    client = openai.AsyncOpenAI(api_key=openai_api_key)
    response = await client.chat.completions.create(
        model="gpt-4o",
        max_tokens=4096,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return _parse_json(response.choices[0].message.content)
