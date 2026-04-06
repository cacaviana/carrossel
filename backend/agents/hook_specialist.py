import json
from pathlib import Path

import anthropic

from utils.json_parser import parse_llm_json

PROMPT_PATH = Path(__file__).parent / "hook-specialist.md"
if not PROMPT_PATH.exists():
    PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "agents" / "hook-specialist.md"


async def executar(
    copy: dict,
    formato: str,
    feedback: str = "",
    claude_api_key: str = "",
) -> dict:
    """Executa o Hook Specialist: gera 3 ganchos A/B/C.

    Retorna: dict com hooks: [{letra, texto, abordagem}]
    """
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""

    brand_ctx = copy.pop("_brand_context", "") if isinstance(copy, dict) else ""
    user_prompt = f"Copy completa:\n{json.dumps(copy, ensure_ascii=False, indent=2)}\n\nFormato: {formato}\n"
    if brand_ctx:
        user_prompt += f"\n=== CONTEXTO DA MARCA ===\n{brand_ctx}\nAdapte os hooks para esta marca, tom e publico.\n=== FIM ===\n"
    if feedback:
        user_prompt += f"\nFEEDBACK DO USUARIO (versao anterior foi rejeitada): {feedback}\n"
        user_prompt += "GERE hooks COMPLETAMENTE DIFERENTES da versao anterior, seguindo o feedback acima.\n"
    # Tamanho do hook varia por formato
    if formato in ("post_unico", "thumbnail_youtube", "capa_reels"):
        user_prompt += (
            "\nATENCAO: Este e um formato de IMAGEM UNICA (nao carrossel). "
            "O hook sera o TEXTO PRINCIPAL que aparece NA IMAGEM. "
            "Deve ser CURTISSIMO: maximo 6-8 palavras. "
            "Exemplos: 'Dia das Maes 15% OFF', 'Mamae merece o melhor', 'Presenteie com amor'. "
            "NAO escreva paragrafos. NAO use emojis. Apenas o texto que vai NA imagem.\n"
        )
    else:
        user_prompt += (
            "\nEste e um carrossel. O hook sera o texto da CAPA (primeiro slide). "
            "Pode ter ate 2 frases curtas (max 15 palavras total).\n"
        )
    user_prompt += "Gere 3 ganchos (A, B, C) com abordagens diferentes. Responda em JSON com array 'hooks'."
    user_prompt += "\nResposta OBRIGATORIAMENTE em JSON valido. Sem comentarios, sem trailing commas."

    client = anthropic.AsyncAnthropic(api_key=claude_api_key)
    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return parse_llm_json(message.content[0].text)
