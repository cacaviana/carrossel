"""Modulo [CTA] do prompt composavel.

Separado MESMO — nao mistura com texto. Tres niveis: inativo, padrao, forte.
"""

_INATIVO = """[CTA]: Inativo

- Nenhuma ação explícita"""

_PADRAO = """[CTA]: Ativo

- Tipo: texto curto
- Máx: 5 palavras

- Exemplos:
  - "salve isso"
  - "veja mais"
  - "comente"

- Posição:
  - final do layout"""

_FORTE = """[CTA]: Forte

- Destaque visual: alto
- Pode usar botão/box

- Posição:
  - base OU slide final (carrossel)

- Ocupação:
  - até 30% do layout"""


def cta_block(forca: str = "padrao") -> str:
    """Retorna o bloco [CTA].

    Args:
        forca: 'inativo' | 'padrao' | 'forte'. Default 'padrao'.

    Returns:
        String com o bloco. Fallback 'padrao' se valor desconhecido.
    """
    if forca == "inativo":
        return _INATIVO
    if forca == "forte":
        return _FORTE
    return _PADRAO
