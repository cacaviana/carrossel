"""Modulo [FORMATO] do prompt composavel.

Estrutura base sem opiniao — so layout puro. Cada formato define dimensoes,
margens, estrutura e limites. Nao fala de cores, pessoa, imagem nem CTA.
"""

FORMATOS = {
    "post_unico": """[FORMATO]: Post único

- Tamanho: 1080x1350
- Margem segura: 120px topo e base

- Estrutura:
  - 1 área principal
  - Fluxo vertical

- Limite:
  - 1 título
  - 1 texto auxiliar
  - 1 CTA (opcional)""",

    "carrossel": """[FORMATO]: Carrossel

- Tamanho: 1080x1350
- Margem segura: 120px topo e base

- Estrutura:
  - Capa (slide 1)
  - Slides internos
  - Slide final (opcional CTA)

- Regras:
  - 1 ideia por slide
  - Máx: 5 blocos por slide""",

    "thumb": """[FORMATO]: Thumb

- Tamanho: 1080x1080

- Estrutura:
  - Impacto imediato

- Limite:
  - 1 título dominante
  - Sem texto auxiliar
  - Sem CTA""",
}


def formato_block(formato_id: str) -> str:
    """Retorna o bloco [FORMATO] pronto pra concatenar no prompt.

    Args:
        formato_id: 'post_unico' | 'carrossel' | 'thumb'

    Returns:
        String com o bloco. Fallback pra 'carrossel' se formato_id desconhecido.
    """
    return FORMATOS.get(formato_id, FORMATOS["carrossel"])
