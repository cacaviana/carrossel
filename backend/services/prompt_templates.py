"""
Prompt templates para geracao de slides — dark mode design system.
Paleta: roxo lilas (#A78BFA), verde neon (#34D399), amber (#FBBF24), vermelho (#F87171).
Fundo: #0A0A0F, cards: #12121A, gradiente: #1a0a2e -> #0a1628.
"""

DESIGN_SYSTEM = (
    "Dark mode premium tech. "
    "Fundo: preto profundo (#0A0A0F), NUNCA 100% preto. "
    "Gradiente sutil diagonal: #1a0a2e (topo esquerdo) para #0a1628 (base direito). "
    "Cards: fundo (#12121A) com borda roxa sutil (rgba(167,139,250,0.2)), radius 14px. "
    "Acento principal: roxo lilas (#A78BFA) para keywords, bordas ativas, pontos focais. "
    "Acento secundario: verde neon (#34D399) para badges de codigo, numeros positivos. "
    "Acento terciario: amber (#FBBF24) para metricas de impacto, atencao. "
    "Acento negativo: vermelho (#F87171) para limitacoes, alertas. "
    "Texto principal: branco (#FFFFFF). Texto secundario: cinza muted (#9896A3). "
    "Fonte editorial: Outfit, Light (300) para titulos, Semibold (600) para destaques. "
    "Fonte tecnica: JetBrains Mono para badges, codigo, metricas. "
    "Glows: circulos com blur extremo e 6-10% opacidade nos cantos para atmosfera. "
    "Estilo: premium, minimalista, tech. SEM emojis. SEM stock vibes. SEM clipart."
)


def build_prompt(slide: dict, position: int, total: int) -> str:
    """Constroi prompt de imagem baseado no tipo e posicao do slide."""
    slide_type = slide.get("type", "content")
    counter = f"{position}/{total}"

    if slide_type == "cover":
        return _cover_prompt(slide)
    if slide_type == "code":
        return _code_prompt(slide, counter)
    if slide_type == "comparison":
        return _comparison_prompt(slide, counter)
    if slide_type == "cta":
        return _cta_prompt(slide)
    return _content_prompt(slide, counter)


def _cover_prompt(slide: dict) -> str:
    headline = slide.get("headline", "")
    subline = slide.get("subline", "")
    return (
        f"Crie slide LinkedIn 4:5 (1080x1350px). DESIGN: {DESIGN_SYSTEM} "
        f"FUNDO: gradiente diagonal (#1a0a2e topo esquerdo para #0a1628 base direito) "
        f"com glows sutis de roxo (#A78BFA, 8% opacidade, blur extremo) nos cantos. "
        f"Badge pill verde (#34D399) no topo: 'Carlos Viana'. "
        f"Borda do badge: 1px #34D399, fundo: #34D399 com 10% opacidade. "
        f"Headline em branco (#FFFFFF), grande, fonte Outfit Light (300), "
        f"com palavras-chave em roxo lilas (#A78BFA) Semibold (600): '{headline}'. "
        f"Subline em cinza muted (#9896A3): '{subline}'. "
        f"Rodape: foto circular com borda roxa (#A78BFA) + 'Carlos Viana' em branco + "
        f"'DESLIZA →' em roxo (#A78BFA) monospace. "
        f"TODO texto deve ser LEGIVEL sobre o fundo escuro."
    )


def _content_prompt(slide: dict, counter: str) -> str:
    title = slide.get("title", "")
    etapa = slide.get("etapa", "")
    bullets = slide.get("bullets", [])
    bullets_text = "\n".join(f"→ {b}" for b in bullets)
    return (
        f"Crie slide LinkedIn 4:5 (1080x1350px). DESIGN: {DESIGN_SYSTEM} "
        f"FUNDO: preto profundo (#0A0A0F). Card central com fundo (#12121A), "
        f"borda 1px roxa sutil (rgba(167,139,250,0.2)), radius 14px. "
        f"Badge pill roxo no topo do card: '{etapa}'. "
        f"Borda: 1px rgba(167,139,250,0.2), fundo: rgba(167,139,250,0.1), texto roxo (#A78BFA). "
        f"Titulo em branco (#FFFFFF), Outfit Semibold: '{title}'. "
        f"Bullets em cinza muted (#9896A3), com palavras-chave em roxo (#A78BFA) bold:\n{bullets_text}\n"
        f"Rodape: foto circular com borda roxa + 'Carlos Viana' + '{counter}' em cinza (#5A5A66) monospace. "
        f"Hierarquia visual clara. Layout limpo."
    )


def _code_prompt(slide: dict, counter: str) -> str:
    code = slide.get("code", "")
    caption = slide.get("caption", "")
    return (
        f"Crie slide LinkedIn 4:5 (1080x1350px). DESIGN: {DESIGN_SYSTEM} "
        f"FUNDO: preto profundo (#0A0A0F). "
        f"Badge pill verde (#34D399) no topo: 'CODIGO REAL'. "
        f"Borda: 1px #34D399, fundo: rgba(52,211,153,0.1), texto verde (#34D399). "
        f"O codigo DEVE estar dentro de uma JANELA DE TERMINAL estilo macOS/Apple: "
        f"Container com borda 1px (#1E1E35), radius 10px, largura 90-95%. "
        f"Barra de titulo: altura 28px, fundo (#1a1a2a), radius superior 10px. "
        f"3 botoes circulares: vermelho #FF5F57, amarelo #FEBC2E, verde #28C840, 10px cada, gap 6px. "
        f"Nome do arquivo centralizado em monospace 10px cinza (#9896A3): 'agent.py'. "
        f"Corpo do terminal: fundo (#0D0D18), radius inferior 10px, padding 24px. "
        f"CODIGO em JetBrains Mono, 9.5px, cor verde (#34D399), line-height 1.55. "
        f"CADA CARACTERE deve ser LEGIVEL. "
        f"Codigo:\n{code}\n"
        f"Caption abaixo da janela em cinza muted (#9896A3): '{caption}'. "
        f"Rodape: foto circular com borda roxa + 'Carlos Viana' + '{counter}' em cinza (#5A5A66) monospace."
    )


def _comparison_prompt(slide: dict, counter: str) -> str:
    left_label = slide.get("left_label", "")
    right_label = slide.get("right_label", "")
    left_items = slide.get("left_items", [])
    right_items = slide.get("right_items", [])
    left_text = ", ".join(left_items)
    right_text = ", ".join(right_items)
    return (
        f"Crie slide LinkedIn 4:5 (1080x1350px). DESIGN: {DESIGN_SYSTEM} "
        f"FUNDO: preto profundo (#0A0A0F). Card central (#12121A), borda roxa sutil. "
        f"Dois blocos lado a lado com gap dentro do card. "
        f"Bloco ESQUERDO: fundo vermelho escuro (rgba(248,113,113,0.09)), "
        f"borda 1px vermelha (rgba(248,113,113,0.15)). "
        f"Header: '{left_label}' em vermelho (#F87171). Items: {left_text}. "
        f"Bloco DIREITO: fundo roxo escuro (rgba(167,139,250,0.1)), "
        f"borda 1px roxa (rgba(167,139,250,0.2)). "
        f"Header: '{right_label}' em roxo (#A78BFA). Items: {right_text}. "
        f"Rodape: foto circular com borda roxa + 'Carlos Viana' + '{counter}' em cinza (#5A5A66) monospace."
    )


def _cta_prompt(slide: dict) -> str:
    headline = slide.get("headline", "")
    subline = slide.get("subline", "")
    tags = slide.get("tags", [])
    tags_text = ", ".join(tags)
    return (
        f"Crie slide LinkedIn 4:5 (1080x1350px). DESIGN: {DESIGN_SYSTEM} "
        f"FUNDO: gradiente diagonal (#1a0a2e para #0a1628) com glows roxos sutis nos cantos. "
        f"Linha horizontal roxa (#A78BFA) fina decorativa no topo. "
        f"Se houver foto da pessoa, colocar no centro com moldura circular (40-48px) "
        f"e borda fina roxa (#A78BFA). Pessoa NATURAL e CONFIANTE. "
        f"Headline em branco (#FFFFFF), Outfit Semibold: '{headline}'. "
        f"Texto em cinza muted (#9896A3): '{subline}'. "
        f"Tags em badges pill com fundo (#12121A), borda roxa sutil, texto roxo (#A78BFA): {tags_text}. "
        f"Rodape: 'Carlos Viana — IT Valley School — Pos IA & ML' em cinza (#9896A3). "
        f"Card de convite com borda roxa sutil."
    )
