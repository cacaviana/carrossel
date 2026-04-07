import asyncio
import json
import os
from pathlib import Path

import anthropic
import openai

AGENTS_DIR = Path(__file__).resolve().parent.parent.parent / "agents"

PROMPT_MAP = {
    "carrossel": AGENTS_DIR / "copywriter-carrossel.md",
    "post_unico": AGENTS_DIR / "copywriter-post-unico.md",
    "thumbnail_youtube": AGENTS_DIR / "copywriter-thumbnail.md",
    "capa_reels": AGENTS_DIR / "copywriter-reels.md",
}
FALLBACK_PROMPT = AGENTS_DIR / "copywriter.md"


def _load_prompt(formato: str) -> str:
    path = PROMPT_MAP.get(formato, FALLBACK_PROMPT)
    if path.exists():
        return path.read_text(encoding="utf-8")
    if FALLBACK_PROMPT.exists():
        return FALLBACK_PROMPT.read_text(encoding="utf-8")
    return ""


def _build_user_prompt(briefing: dict, formato: str, feedback: str) -> str:
    # Extrair brand context se existir
    brand_ctx = briefing.pop("_brand_context", "")

    user_prompt = f"Briefing aprovado:\n{json.dumps(briefing, ensure_ascii=False, indent=2)}\n\nFormato: {formato}\n"

    if brand_ctx:
        user_prompt += (
            f"\n=== CONTEXTO DA MARCA (OBRIGATORIO — substitui qualquer persona padrao) ===\n"
            f"{brand_ctx}\n"
            f"IMPORTANTE: Use EXATAMENTE o tom, linguagem e persona descritos acima. "
            f"NAO use persona de outra marca. Use EXATAMENTE a persona descrita acima. "
            f"Adapte TUDO para esta marca.\n"
            f"=== FIM CONTEXTO DA MARCA ===\n"
        )

    if feedback:
        user_prompt += f"\nFEEDBACK DO USUARIO (versao anterior rejeitada): {feedback}\n"
        user_prompt += "GERE copy COMPLETAMENTE DIFERENTE, seguindo o feedback acima.\n"
    FORMATOS_SLIDE_UNICO = ("post_unico", "thumbnail_youtube", "capa_reels")
    if formato in FORMATOS_SLIDE_UNICO:
        user_prompt += f"ATENCAO: formato '{formato}' = APENAS 1 SLIDE. Gere exatamente 1 slide. NAO gere multiplos slides."
        user_prompt += " Responda em JSON."
    else:
        user_prompt += "Gere a copy completa com NO MAXIMO 7 slides. Responda em JSON."
    user_prompt += "\nResposta OBRIGATORIAMENTE em JSON valido. Sem comentarios, sem trailing commas."
    return user_prompt


from utils.json_parser import parse_llm_json


async def _gerar_anthropic(system_prompt: str, user_prompt: str, api_key: str) -> dict:
    client = anthropic.AsyncAnthropic(api_key=api_key)
    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        temperature=0.9,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    result = parse_llm_json(message.content[0].text)
    result["_provider"] = "anthropic"
    result["_model"] = "claude-sonnet-4"
    return result


async def _gerar_openai(system_prompt: str, user_prompt: str, api_key: str) -> dict:
    client = openai.AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
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
    result["_model"] = "gpt-4o"
    return result


async def executar(
    briefing: dict,
    formato: str,
    feedback: str = "",
    claude_api_key: str = "",
) -> dict:
    """Executa o Copywriter via Anthropic (Claude)."""
    system_prompt = _load_prompt(formato)
    user_prompt = _build_user_prompt(briefing, formato, feedback)

    if not claude_api_key:
        claude_api_key = os.getenv("CLAUDE_API_KEY", "")

    return await _gerar_anthropic(system_prompt, user_prompt, claude_api_key)
