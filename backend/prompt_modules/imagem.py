"""Modulo [IMAGEM] do prompt composavel.

Totalmente independente do formato. Controla se tem imagem no slide,
quanto ocupa, onde fica, e as regras de legibilidade.
"""

_ATIVA_TEMPLATE = """[IMAGEM]: Ativa

- Obrigatória: sim
- Ocupação: {ocupacao}
- Posição:
  - {posicao}

- Regras:
  - Não cobrir legibilidade do texto
  - Manter contraste"""

_INATIVA = """[IMAGEM]: Inativa

- Layout: 100% tipográfico

- Regras:
  - Usar contraste forte
  - Usar hierarquia de fonte
  - Pode usar shapes simples"""


def imagem_block(
    ativa: bool = True,
    ocupacao: str = "40–60%",
    posicao: str = "topo OU fundo OU lateral",
) -> str:
    """Retorna o bloco [IMAGEM].

    Args:
        ativa: True gera bloco 'Ativa', False gera 'Inativa' (100% tipografico).
        ocupacao: Faixa de ocupacao da imagem (ignorado se ativa=False).
        posicao: Posicao permitida (ignorado se ativa=False).

    Returns:
        String com o bloco.
    """
    if not ativa:
        return _INATIVA
    return _ATIVA_TEMPLATE.format(ocupacao=ocupacao, posicao=posicao)
