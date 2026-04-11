"""Modulo [TEXTO] do prompt composavel.

Hierarquia titulo > auxiliar. Limites rigidos de palavras por papel.
"""

_TEXTO_PADRAO = """[TEXTO]

Título:
- Máx: 8 palavras
- Papel: chamar atenção
- Tamanho: dominante

Texto auxiliar:
- Máx: 2–3 linhas
- Papel: complementar
- Não repetir título"""


def texto_block() -> str:
    """Retorna o bloco [TEXTO] fixo."""
    return _TEXTO_PADRAO
