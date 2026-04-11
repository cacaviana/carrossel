"""Composer dos 7 modulos de prompt — concatena na ordem oficial.

Ordem:  FORMATO + IMAGEM + TEXTO + CTA + REGRAS + DNA + TRAVA

O DNA so entra se a marca tiver o campo preenchido. TRAVA sempre fecha.

NENHUMA integracao com PromptComposer ainda — esse modulo existe isolado
na Fase 0 pra ser inspecionado antes de ligar em producao (Fase 6).
"""

from prompt_modules.formato import formato_block
from prompt_modules.imagem import imagem_block
from prompt_modules.texto import texto_block
from prompt_modules.cta import cta_block
from prompt_modules.regras import regras_block
from prompt_modules.dna import dna_block
from prompt_modules.trava import trava_block


def montar(
    formato_id: str,
    brand: dict | None = None,
    imagem_ativa: bool = True,
    imagem_ocupacao: str = "40–60%",
    imagem_posicao: str = "topo OU fundo OU lateral",
    cta_forca: str = "padrao",
) -> str:
    """Monta o prompt composto a partir dos 7 blocos.

    Args:
        formato_id: 'post_unico' | 'carrossel' | 'thumb'
        brand: dict do brand profile (usado so pelo bloco DNA)
        imagem_ativa: True = bloco [IMAGEM]: Ativa; False = Inativa
        imagem_ocupacao: faixa de ocupacao (so usado se imagem_ativa=True)
        imagem_posicao: posicao permitida (so usado se imagem_ativa=True)
        cta_forca: 'inativo' | 'padrao' | 'forte'

    Returns:
        String final do prompt composto, pronta pra enviar ao Gemini.
    """
    blocos = [
        formato_block(formato_id),
        imagem_block(ativa=imagem_ativa, ocupacao=imagem_ocupacao, posicao=imagem_posicao),
        texto_block(),
        cta_block(cta_forca),
        regras_block(),
    ]

    dna = dna_block(brand)
    if dna:
        blocos.append(dna)

    blocos.append(trava_block())

    return "\n\n".join(blocos)
