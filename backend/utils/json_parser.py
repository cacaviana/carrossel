import json
import re


def parse_llm_json(text: str) -> dict:
    """Extrai JSON da resposta de um LLM (Claude, OpenAI, etc).

    Trata: code fences, trailing commas, comments JS, texto antes/depois do JSON.
    Retorna dict parseado ou {"raw_text": text} como fallback.
    """
    # 1. Tentar extrair de code fence ```json ... ```
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            text = fence_match.group(1)

    # 2. Encontrar o JSON bruto no texto
    start = text.find("{")
    end = text.rfind("}") + 1
    if start < 0 or end <= 0:
        return {"raw_text": text}

    json_str = text[start:end]

    # 3. Tentar parse direto
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # 4. Limpar JSON malformado (trailing commas, comments)
    cleaned = re.sub(r",\s*}", "}", json_str)
    cleaned = re.sub(r",\s*]", "]", cleaned)
    cleaned = re.sub(r"//.*?\n", "\n", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"raw_text": text}
