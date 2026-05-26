def gerar_variacoes(prompt: str) -> list[str]:
    """Gera 3 variacoes de prompt via manipulacao de string (sem LLM).

    Estrategia:
    - Variacao 1: prompt original
    - Variacao 2: estilo mais minimalista
    - Variacao 3: estilo mais dramatico

    Retorna: lista de 3 prompts.
    """
    v1 = prompt
    v2 = _variacao_minimalista(prompt)
    v3 = _variacao_dramatica(prompt)
    return [v1, v2, v3]


def _variacao_minimalista(prompt: str) -> str:
    prefix = "Minimalist style. Clean, simple composition with generous whitespace. "
    return prefix + prompt


def _variacao_dramatica(prompt: str) -> str:
    prefix = "Dramatic, high-contrast style. Bold shadows, vibrant accent colors, cinematic lighting. "
    return prefix + prompt
