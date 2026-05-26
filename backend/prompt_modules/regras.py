"""Modulo [REGRAS] do prompt composavel.

Regras gerais SEMPRE aplicadas, independente de formato/imagem/cta.
"""

_REGRAS_GLOBAIS = """[REGRAS]

- Priorizar leitura mobile
- Não encostar texto nas bordas
- Alto contraste sempre
- Não poluir visual
- Respeitar hierarquia:
  título > auxiliar > CTA"""


def regras_block() -> str:
    """Retorna o bloco [REGRAS] fixo."""
    return _REGRAS_GLOBAIS
