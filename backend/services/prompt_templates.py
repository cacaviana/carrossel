"""DEPRECATED: usar PromptComposer. Ver factories/prompt_composer.py

Prompt templates para geracao de slides — dark mode design system.
Paleta: roxo lilas (#A78BFA), verde neon (#34D399), amber (#FBBF24), vermelho (#F87171).
Fundo: #0A0A0F, cards: #12121A, gradiente: #1a0a2e -> #0a1628.

Este modulo inteiro esta deprecado. A funcao build_prompt() foi substituida
pelo PromptComposer (4 camadas composable). As constantes FOTO_INSTRUCTION_THUMBNAIL
e DESIGN_SYSTEM ainda sao referenciadas por brand_prompt_builder e podem ser
removidas quando aquele modulo tambem migrar.
"""

from utils.dimensions import get_dims, get_prompt_size_str

FOTO_INSTRUCTION = ""

FOTO_INSTRUCTION_THUMBNAIL = (
    "Draw a LARGE photorealistic portrait of a young male tech creator (beard, friendly smile) "
    "occupying 40% of the right side of the image. Strong facial expression (excited/surprised). "
    "This is a YouTube thumbnail — the creator's face is the MAIN element. "
    "Face must be well-lit, high contrast, looking at camera."
)

DESIGN_SYSTEM = (
    "Dark mode premium cinematico. "
    "Fundo: preto profundo (#0A0A0F) com gradiente diagonal roxo/azul escuro. "
    "O fundo deve ter PROFUNDIDADE — luzes difusas roxas e azuis com bokeh, "
    "como pontos de luz desfocados em diferentes camadas. NAO chapado. "
    "OBRIGATORIO: uma ilustracao 3D wireframe em linhas neon roxas (#A78BFA) com glow sutil, "
    "representando algo tech (globo terrestre, rede neural, estrutura molecular, etc). "
    "As linhas devem ser FINAS e LUMINOSAS, estilo holograma. "
    "Cards: efeito glassmorphism (vidro fosco semi-transparente, backdrop-blur, borda roxa sutil). "
    "Acento principal: roxo lilas (#A78BFA). Acento secundario: verde neon (#34D399). "
    "Texto principal: branco (#FFFFFF). Texto secundario: cinza muted (#9896A3). "
    "Palavras-chave em negrito branco ou roxo (#A78BFA). "
    "Estilo: premium, minimalista, tech, cinematico. SEM emojis. SEM clipart. SEM icones flat."
)


def build_prompt(slide: dict, position: int, total: int, design_system: str | None = None, formato: str = "carrossel") -> str:
    """DEPRECATED: usar PromptComposer. Ver factories/prompt_composer.py

    Constroi prompt de imagem baseado no tipo e posicao do slide.
    """
    ds = design_system or DESIGN_SYSTEM
    slide_type = slide.get("type", "content")
    counter = f"{position}/{total}"
    size_str = get_prompt_size_str(formato)
    dims = get_dims(formato)
    ratio = dims["ratio"]

    # Thumbnail YouTube — prompt especial com avatar GRANDE
    if formato == "thumbnail_youtube":
        return _thumbnail_prompt(slide, ds, size_str, ratio)

    # Slides com ilustração
    illustration = slide.get("illustration_description", "")
    if illustration:
        return _visual_prompt(slide, counter, ds, illustration, size_str, ratio)

    if slide_type == "infographic":
        return _infographic_prompt(slide, ds, size_str, ratio)
    if slide_type == "cover":
        return _cover_prompt(slide, ds, size_str, ratio)
    if slide_type == "code":
        return _code_prompt(slide, counter, ds, size_str, ratio)
    if slide_type == "comparison":
        return _comparison_prompt(slide, counter, ds, size_str, ratio)
    if slide_type == "cta":
        return _cta_prompt(slide, ds, size_str, ratio)
    return _content_prompt(slide, counter, ds, size_str, ratio)


def _cover_prompt(slide: dict, ds: str, size_str: str = "1080x1350px, 4:5 portrait", ratio: str = "4:5") -> str:
    headline = slide.get("headline", "")
    subline = slide.get("subline", "")
    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). {ds} "
        f"Badge pill verde (#34D399) no topo: 'Carlos Viana'. "
        f"Headline ENORME em branco, ocupando a maior parte do slide, "
        f"com palavras-chave em roxo (#A78BFA) bold: '{headline}'. "
        f"Subline em cinza (#9896A3): '{subline}'. "
        f"Na parte inferior do slide: uma ilustracao 3D wireframe em linhas neon roxas "
        f"(ex: globo terrestre, rede de dados, estrutura tech) com glow sutil. "
        f"Rodape: apenas texto 'Carlos Viana' no canto inferior. "
        f"Ao lado: 'Carlos Viana' + '1/N'. "
        f"TODO texto LEGIVEL."
    )


def _content_prompt(slide: dict, counter: str, ds: str, size_str: str = "1080x1350px, 4:5 portrait", ratio: str = "4:5") -> str:
    title = slide.get("title", "")
    etapa = slide.get("etapa", "")
    bullets = slide.get("bullets", [])
    bullets_text = "\n".join(f"→ {b}" for b in bullets)
    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). {ds} "
        f"Card central GRANDE glassmorphism (vidro fosco semi-transparente, borda roxa sutil). "
        f"Badge pill roxo no topo do card: '{etapa}'. "
        f"Titulo GRANDE em branco bold: '{title}'. "
        f"Bullets em branco/cinza, palavras-chave em negrito ou roxo (#A78BFA):\n{bullets_text}\n"
        f"No fundo atras do card: wireframe 3D neon roxo sutil (holograma tech). "
        f"Rodape: apenas texto 'Carlos Viana' + '{counter}' no canto inferior. "
        f"Texto LEGIVEL."
    )


def _code_prompt(slide: dict, counter: str, ds: str, size_str: str = "1080x1350px, 4:5 portrait", ratio: str = "4:5") -> str:
    code = slide.get("code", "")
    caption = slide.get("caption", "")
    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). DESIGN: {ds} "
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
        f"Rodape: apenas texto 'Carlos Viana' + '{counter}' no canto inferior."
    )


def _comparison_prompt(slide: dict, counter: str, ds: str, size_str: str = "1080x1350px, 4:5 portrait", ratio: str = "4:5") -> str:
    left_label = slide.get("left_label", "")
    right_label = slide.get("right_label", "")
    left_items = slide.get("left_items", [])
    right_items = slide.get("right_items", [])
    left_text = ", ".join(left_items)
    right_text = ", ".join(right_items)
    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). DESIGN: {ds} "
        f"FUNDO: preto profundo (#0A0A0F). Card central (#12121A), borda roxa sutil. "
        f"Dois blocos lado a lado com gap dentro do card. "
        f"Bloco ESQUERDO: fundo vermelho escuro (rgba(248,113,113,0.09)), "
        f"borda 1px vermelha (rgba(248,113,113,0.15)). "
        f"Header: '{left_label}' em vermelho (#F87171). Items: {left_text}. "
        f"Bloco DIREITO: fundo roxo escuro (rgba(167,139,250,0.1)), "
        f"borda 1px roxa (rgba(167,139,250,0.2)). "
        f"Header: '{right_label}' em roxo (#A78BFA). Items: {right_text}. "
        f"Rodape: apenas texto 'Carlos Viana' + '{counter}' no canto inferior."
    )


def _cta_prompt(slide: dict, ds: str, size_str: str = "1080x1350px, 4:5 portrait", ratio: str = "4:5") -> str:
    headline = slide.get("headline", "")
    subline = slide.get("subline", "")
    tags = slide.get("tags", [])
    tags_text = ", ".join(tags)
    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). {ds} "
        f"Headline GRANDE em branco bold: '{headline}'. "
        f"Texto em cinza (#9896A3): '{subline}'. "
        f"Tags em badges pill glassmorphism com texto roxo (#A78BFA): {tags_text}. "
        f"Wireframe 3D neon roxo sutil no fundo (globo, rede, holograma). "
        f"Rodape: 'Carlos Viana — IT Valley School — Pos IA & ML' em cinza. "
        f"Atmosfera cinematica, premium."
    )


def _visual_prompt(slide: dict, counter: str, ds: str, illustration: str, size_str: str = "1080x1350px, 4:5 portrait", ratio: str = "4:5") -> str:
    title = slide.get("title", slide.get("headline", ""))
    return (
        f"Crie slide LinkedIn {ratio} ({size_str}). DESIGN: {ds} "
        f"FUNDO: preto profundo (#0A0A0F). "
        f"Titulo em branco (#FFFFFF), Outfit Semibold, CURTO: '{title}'. "
        f"A MAIOR PARTE DO SLIDE deve ser ocupada por uma ILUSTRACAO/DIAGRAMA tecnico: "
        f"{illustration} "
        f"Use as cores do design system para o diagrama: roxo (#A78BFA) para linhas e setas, "
        f"verde (#34D399) para highlights positivos, amber (#FBBF24) para metricas, "
        f"branco para labels, cinza (#9896A3) para texto secundario. "
        f"O diagrama deve ser CLARO, PROFISSIONAL e LEGIVEL. "
        f"Rodape: apenas texto 'Carlos Viana' + '{counter}' no canto inferior."
    )


def _infographic_prompt(slide: dict, ds: str, size_str: str = "1080x1350px, 4:5 portrait", ratio: str = "4:5") -> str:
    title = slide.get("title", slide.get("headline", ""))
    illustration = slide.get("illustration_description", "")
    bullets = slide.get("bullets", [])
    bullets_text = " | ".join(bullets) if bullets else ""
    return (
        f"Crie INFOGRAFICO LinkedIn {ratio} ({size_str}). DESIGN: {ds} "
        f"FUNDO: preto profundo (#0A0A0F) com gradiente sutil diagonal. "
        f"Titulo GRANDE no topo em branco (#FFFFFF), Outfit Semibold: '{title}'. "
        f"LAYOUT INFOGRAFICO DENSO E VISUAL com multiplas secoes: "
        f"{illustration} "
        f"METRICAS/DADOS destacados com numeros GRANDES (28px+) em cards coloridos: "
        f"roxo (#A78BFA), verde (#34D399), amber (#FBBF24). "
        f"Secoes separadas com linhas finas ou cards (#12121A) com borda roxa sutil. "
        f"Dados adicionais: {bullets_text}. "
        f"Icones clean (outline, fundo #16162A, radius). SEM emojis. SEM clipart. "
        f"Rodape: apenas texto 'Carlos Viana — IT Valley School' no canto inferior. "
        f"O slide deve ser RICO visualmente, com muita informacao organizada de forma clara."
    )


# Anuncio (pos-pivot 2026-04-23): mesma dimensao do post_unico (1080x1350).
# Nao ha build_anuncio_prompt dedicado -- o anuncio usa o mesmo pipeline
# de imagem do post_unico via PromptComposer.


def _thumbnail_prompt(slide: dict, ds: str, size_str: str = "1280x720px, 16:9 landscape", ratio: str = "16:9") -> str:
    headline = slide.get("headline", "") or slide.get("title", "") or slide.get("titulo", "")
    subline = slide.get("subline", "") or slide.get("corpo", "") or slide.get("conteudo", "")
    # Buscar em elementos se vazio
    if not headline and isinstance(slide.get("elementos"), list):
        for el in slide["elementos"]:
            t = el.get("tipo", "")
            if "titulo" in t:
                headline = el.get("texto", el.get("conteudo", ""))
                if isinstance(headline, list):
                    headline = " ".join(x.get("texto", "") if isinstance(x, dict) else str(x) for x in headline)
                break
    if not headline:
        headline = subline or "TECH"
    return (
        f"YouTube thumbnail, {ratio} horizontal landscape ({size_str}). "
        f"LAYOUT: RIGHT SIDE (40% of image) = {FOTO_INSTRUCTION_THUMBNAIL} "
        f"LEFT SIDE (60% of image) = HUGE bold text: '{headline}' in white (#FFFFFF) with black outline/shadow. "
        f"Font: ultra bold, massive, filling the left side. "
        f"Background: vibrant gradient, NOT dark — use bright saturated colors (electric blue, orange, purple). "
        f"High contrast, eye-catching, designed to maximize click-through rate. "
        f"Style: modern YouTube thumbnail 2024/2025. Clean, impactful, professional. "
        f"NO small text. NO decorative elements that distract from face + text. "
        f"The creator's face and the big text are the ONLY two elements."
    )
