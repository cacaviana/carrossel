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


def cta_block(forca: str = "padrao", texto: str = "") -> str:
    """Retorna o bloco [CTA].

    Args:
        forca: 'inativo' | 'padrao' | 'forte'. Default 'padrao'.
        texto: texto literal do CTA travado pelo user. Quando preenchido,
            anexa instrucao pro Gemini renderizar esse texto exato no botao.

    Returns:
        String com o bloco. Fallback 'padrao' se valor desconhecido.
    """
    if forca == "inativo" and not texto:
        return _INATIVO
    base = _FORTE if (forca == "forte" or texto) else _PADRAO
    if texto:
        base += (
            f"\n\n- TEXTO EXATO DO BOTAO: \"{texto}\""
            f"\n- Renderizar como BOTAO/BADGE em destaque, alto contraste"
            f"\n- NAO traduzir, NAO encurtar, NAO inventar variacao"
            f"\n- Usar literalmente \"{texto}\" caractere por caractere"
        )
    return base
