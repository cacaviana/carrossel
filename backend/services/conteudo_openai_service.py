import openai

from factories.conteudo_factory import build_system_prompt, build_user_prompt
from utils.json_parser import parse_llm_json


async def gerar_conteudo_openai(
    openai_api_key: str,
    disciplina: str | None = None,
    tecnologia: str | None = None,
    tema_custom: str | None = None,
    texto_livre: str | None = None,
    total_slides: int = 10,
    tipo_carrossel: str = "texto",
) -> dict:
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(disciplina, tecnologia, tema_custom, texto_livre, total_slides, tipo_carrossel)

    client = openai.AsyncOpenAI(api_key=openai_api_key)
    response = await client.chat.completions.create(
        model="gpt-5.4-mini",
        max_completion_tokens=4096,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return parse_llm_json(response.choices[0].message.content)
