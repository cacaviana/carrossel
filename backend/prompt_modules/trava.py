"""Modulo [TRAVA] do prompt composavel.

Instrucao final anti-alucinacao. ENTRA SEMPRE no final do prompt.
"""

_TRAVA_FINAL = """[TRAVA]

- Não alterar estrutura
- Não reinterpretar layout
- Apenas preencher conteúdo
- Respeitar todos os limites definidos"""


def trava_block() -> str:
    """Retorna o bloco [TRAVA] fixo."""
    return _TRAVA_FINAL
