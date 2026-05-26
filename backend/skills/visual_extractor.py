"""Skill de extracao visual profunda — analisa uma imagem de referencia e extrai
TODOS os detalhes visuais como um diretor de arte dissecando o DNA visual."""

import json
import httpx
from utils.constants import GEMINI_API_URL


PROMPT = """Voce e o melhor diretor de arte do mundo. Acabaram de te mostrar essa imagem e disseram:
"Preciso replicar EXATAMENTE esse estilo visual em outros posts. Disseca tudo."

Voce precisa ser OBSESSIVO com cada detalhe. Nao generalize. Nao chute. Descreva o que voce VE.

IMPORTANTE SOBRE FONTES:
- NUNCA diga Poppins, Inter, Roboto, Open Sans, Lato ou Montserrat a menos que REALMENTE sejam essas
- Se a fonte tem cantos REDONDOS e ar FOFO: provavelmente e Quicksand, Comfortaa, Nunito, Varela Round, Baloo 2
- Se parece MANUSCRITA/HANDWRITTEN: Caveat, Patrick Hand, Kalam, Indie Flower, Pangolin, Shadows Into Light
- Se e BUBBLE/INFLADA/PLAYFUL: Bubblegum Sans, Chewy, Fredoka One, Lilita One, Boogaloo
- Se e CURSIVA/SCRIPT: Dancing Script, Pacifico, Sacramento, Satisfy, Great Vibes
- Se parece IRREGULAR/FEITA A MAO com tracos grossos: e handwritten bubble font (Mochiy Pop P One, Fredoka One)
- Descreva as CARACTERISTICAS da letra: cantos redondos? tracos grossos? levemente irregular? inflada?

DETALHE CRUCIAL sobre tipografia CUTE/HANDWRITTEN:
- NAO e so "bubble font" — tem LEVE IRREGULARIDADE (como feito a mao)
- Tracking levemente apertado, letras NAO perfeitamente alinhadas
- Keyword: "slightly hand-drawn, not perfectly geometric, with subtle irregular spacing"

DETALHE CRUCIAL sobre composicao:
- Elementos decorativos NAO sao aleatorios — eles GUIAM O OLHAR
- Descreva posicao EXATA (orbitando ao redor do sujeito, nao espalhados)
- Fundo pode variar: branco puro, bege, grid pattern em cinza claro
- Feeling: descreva se e "creator friendly", "tutorial", "dica", etc

RETORNE JSON com esta estrutura:

{
    "resumo": "1 frase matadora descrevendo a estetica (ex: 'Soft pastel aesthetic com tipografia handwritten bubble, doodles fofos e composicao airy minimalista')",

    "estetica": "nome da estetica (ex: 'soft girl pastel', 'dark tech premium', 'cottagecore cute', 'corporate clean')",
    "vibe": "3 palavras que definem o sentimento (ex: 'fofo, aconchegante, natural')",

    "dna_cores": {
        "narrativa": "descreva as cores como um diretor de arte falaria (ex: 'Paleta inteiramente pastel suave — rosa bebe, azul claro, verde menta, bege quentinho. Fundo quase branco/off-white. Contraste proposital baixo, tudo muito airy e clean. Nada forte ou saturado.')",
        "paleta_hex": ["#hex1", "#hex2", "#hex3", "#hex4", "#hex5", "#hex6"],
        "fundo": "#hex e descricao",
        "destaque_principal": "#hex e onde aparece",
        "destaque_secundario": "#hex e onde aparece",
        "texto_escuro": "#hex (cor do texto sobre fundo claro)",
        "texto_claro": "#hex (cor do texto sobre fundo escuro, se existir)",
        "erros_evitar": "que cores NUNCA usar nesse estilo (ex: 'Nada saturado, nada neon, nada com contraste forte')"
    },

    "dna_tipografia": {
        "narrativa": "descreva a tipografia como um diretor de arte (ex: 'Fonte handwritten bubbly, levemente irregular como feita a mao. Caixa MAIUSCULA, espessura media/grossa, cantos bem arredondados, levemente inflada — aquele ar fofo. NAO e uma sans-serif limpa tipo Poppins, e uma fonte com PERSONALIDADE, com tracos organicos.')",
        "titulo_fonte_google": "nome EXATO no Google Fonts (ex: Fredoka One, Bubblegum Sans, Quicksand, Caveat)",
        "titulo_caracteristicas": "peso, caixa, tamanho, espacamento, efeitos",
        "corpo_fonte_google": "nome EXATO no Google Fonts para texto de corpo",
        "corpo_caracteristicas": "peso, estilo",
        "keywords_pra_ia": "palavras-chave que uma IA geradora precisa pra replicar essa tipografia (ex: 'handwritten bubble font, cute rounded typography, playful soft lettering, hand drawn text, pastel aesthetic font')",
        "google_fonts_url": "URL completa de import (ex: https://fonts.googleapis.com/css2?family=Fredoka+One&family=Quicksand:wght@400;600&display=swap)",
        "erros_evitar": "que fontes/estilos NUNCA usar (ex: 'Nada muito perfeito ou geometric. Tem que ser levemente irregular. Nada fino ou elegante demais — aqui e FOFO, nao chique.')"
    },

    "dna_composicao": {
        "narrativa": "descreva o layout como um diretor de arte (ex: 'Pessoa central segurando um objeto, fundo minimalista clean. Texto grande sobreposto como overlay. Elementos graficos flutuando ao redor. Muito espaco negativo, composicao airy.')",
        "estrutura": "como os elementos estao organizados de cima pra baixo",
        "alinhamento": "centro/esquerda/direita/misto",
        "espacamento": "apertado/medio/generoso/enorme + descricao",
        "hierarquia": "o que chama atencao primeiro, segundo, terceiro"
    },

    "dna_elementos": {
        "narrativa": "descreva CADA elemento decorativo (ex: 'Estrelinhas sparkle, rabiscos squiggle, shapes organicos, mini icones de coracoes e setas, grids leves. Tudo com ar de feito a mao, nada perfeito demais.')",
        "lista": ["cada elemento que voce ve — stickers, doodles, icones, formas, texturas, bordas, sombras"],
        "keywords_pra_ia": "palavras-chave pra IA gerar esses elementos (ex: 'doodles, sparkles, cute stickers, soft shapes, aesthetic icons, squiggles')",
        "estilo_foto": "se tem foto: iluminacao, estilo, pose, crop (ex: 'Iluminacao natural, look lifestyle, levemente desaturado, clean + cozy')",
        "erros_evitar": "o que NAO colocar (ex: 'Nada 3D realista. Nada com sombra forte. Nada corporate.')"
    },

    "foto_pessoa": {
        "tem": true,
        "descricao": "como a pessoa aparece (ex: 'Jovem mulher sentada em quarto clean, segurando tablet, olhando pra camera com sorriso natural')",
        "posicao": "onde na imagem",
        "estilo": "lifestyle/profissional/casual/editorial"
    },

    "formato": "carrossel 4:5 / post 1:1 / stories 9:16 / thumbnail 16:9",

    "prompt_perfeito": "PROMPT COMPLETO e DETALHADO (MINIMO 300 palavras) que uma IA geradora de imagem usaria pra replicar esse estilo PIXEL POR PIXEL. Inclua TUDO: descricao da cena, estilo de tipografia com keywords E nome de fonte, cores com hex EXATO, elementos decorativos com posicao, composicao detalhada, iluminacao, textura. INCLUA OBRIGATORIAMENTE: 1) 'Text should feel slightly hand-drawn, not perfectly geometric, with subtle irregular spacing' (se aplicavel), 2) Posicao EXATA dos elementos (orbitando, flutuando, guiando o olhar), 3) 'Add subtle grain texture and soft shadows for depth' (se aplicavel), 4) 'The overall mood should feel [descreva o feeling exato]'. Escreva como prompt PRONTO pra DALL-E/Gemini/Midjourney.",

    "hack_consistencia": "REGRAS de consistencia entre posts: O QUE MANTER FIXO (tipografia, paleta, estilo de elementos) vs O QUE VARIAR (posicao do texto, cor dominante, pose, tipo de post). Explique como criar o efeito 'mesma marca mas nunca cansa'.",

    "regras_feed": {
        "variacao": "Each post should vary slightly in composition, color dominance, and text placement while maintaining the same visual identity. Avoid identical layouts across posts.",
        "hierarquia_visual": "Create visual hierarchy by varying title sizes, color intensity, and amount of decorative elements across posts. Alguns posts mais chamativos, outros mais leves.",
        "tipografia_inteligente": "Do not use all font styles in every post. Use display font for main titles only. Use handwritten or cursive font sparingly for emphasis words only. Isso evita post poluido e infantil.",
        "limite_elementos": "Limit decorative elements per post to 3-6 max, placed intentionally to guide the viewer's eye. Nunca encher de doodles aleatorios.",
        "foto_pessoa": "Photos should have consistent lighting (soft natural light), neutral backgrounds, and similar framing (waist-up or centered portrait). Sempre o mesmo estilo de foto."
    },

    "brand_profile": {
        "cores_aplicar": {
            "fundo": "#hex",
            "gradiente_de": "#hex",
            "gradiente_ate": "#hex",
            "card": "#hex",
            "card_borda": "rgba(...)",
            "acento_principal": "#hex",
            "acento_secundario": "#hex",
            "texto_principal": "#hex (DEVE ter contraste com fundo! Se fundo claro, texto ESCURO. NUNCA branco em fundo claro.)",
            "texto_secundario": "#hex"
        },
        "fontes_aplicar": {
            "titulo": "Nome Google Fonts (NUNCA Poppins/Inter se nao for realmente)",
            "corpo": "Nome Google Fonts",
            "codigo": "JetBrains Mono",
            "google_fonts": "URL import completa"
        },
        "visual_aplicar": {
            "estilo_fundo": "instrucao DETALHADA pro fundo (inclua cores hex, texturas, efeitos)",
            "estilo_desenho": "instrucao DETALHADA pras ilustracoes/doodles/elementos decorativos",
            "estilo_card": "instrucao DETALHADA pros cards/containers",
            "estilo_texto": "instrucao DETALHADA pra tipografia (inclua keywords de estilo)",
            "regras_extras": "TUDO que a IA precisa saber: o que SEMPRE fazer + o que NUNCA fazer"
        }
    }
}

RESPONDA APENAS O JSON. Sem markdown. Sem explicacao fora do JSON."""


async def extrair(imagem_b64: str, api_key: str) -> dict:
    """Extrai todos os detalhes visuais de uma imagem de referencia."""
    clean = imagem_b64.split(",")[-1] if "," in imagem_b64 else imagem_b64

    payload = {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": "image/png", "data": clean}},
            {"text": PROMPT},
        ]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }

    model = "gemini-2.5-flash"
    url = GEMINI_API_URL.format(model=model)

    async with httpx.AsyncClient(timeout=90.0) as client:
        res = await client.post(url, json=payload, headers={"x-goog-api-key": api_key})
        res.raise_for_status()
        data = res.json()

    text = ""
    for candidate in data.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if "text" in part:
                text += part["text"]

    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    return json.loads(text.strip())
