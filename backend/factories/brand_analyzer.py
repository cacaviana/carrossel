import json

import httpx

from utils.constants import GEMINI_API_URL


class BrandAnalyzer:

    @staticmethod
    async def analisar(imagens_b64: list[str], nome_marca: str, descricao: str, api_key: str) -> dict:
        """Analisa imagens de referencia via Gemini Vision e extrai brand profile."""

        if not imagens_b64:
            raise ValueError("Envie ao menos 1 imagem de referencia")

        prompt = """Analise estas imagens de referencia visual e extraia um design system completo.

Voce deve identificar:
1. PALETA DE CORES: extraia as cores dominantes, secundarias, de destaque e de fundo. Retorne em hex.
2. ESTILO VISUAL: descreva o estilo (minimalista, terroso, neon, aquarela, flat, 3D, etc)
3. ATMOSFERA: descreva a sensacao que as imagens transmitem
4. TIPO DE ELEMENTO DECORATIVO: que tipo de ilustracao/elemento combina (wireframe, aquarela, foto, icone, etc)
5. ESTILO DE CARD: como seriam cards nesse estilo (cores, bordas, blur, etc)
6. ESTILO DE TEXTO: como seria a tipografia (cores, peso, sombra, etc)

""" + (f"A marca se chama: {nome_marca}. " if nome_marca else "") + (f"Descricao: {descricao}. " if descricao else "") + """

RETORNE APENAS JSON VALIDO neste formato exato (sem markdown, sem explicacao):
{
    "cores": {
        "fundo": "#hex (cor dominante escura do fundo)",
        "gradiente_de": "#hex",
        "gradiente_ate": "#hex",
        "card": "#hex (levemente mais claro que fundo)",
        "card_borda": "rgba(r,g,b,0.2)",
        "acento_principal": "#hex (cor de destaque principal)",
        "acento_secundario": "#hex (segunda cor de destaque)",
        "acento_terciario": "#hex (terceira cor, opcional)",
        "acento_negativo": "#F87171",
        "texto_principal": "#hex (cor do texto principal, geralmente claro)",
        "texto_secundario": "#hex (cor do texto secundario)"
    },
    "visual": {
        "estilo_fundo": "descricao detalhada do fundo ideal baseado nas referencias",
        "estilo_elemento": {
            "tipo": "tipo de ilustracao (aquarela, wireframe, foto, icone line-art, etc)",
            "linhas": "descricao das linhas/tracos",
            "complexidade": "baixa/media/alta com exemplos",
            "profundidade": "descricao da profundidade visual",
            "opacidade": "descricao da opacidade",
            "tematico": "como o elemento se relaciona com o tema do post"
        },
        "estilo_card": "descricao detalhada do estilo de card",
        "estilo_texto": "descricao detalhada do estilo tipografico",
        "estilo_desenho": "descricao do tipo de desenho/ilustracao que combina",
        "regras_extras": "regras visuais adicionais importantes (o que evitar, o que priorizar)"
    },
    "atmosfera": "descricao da atmosfera geral em 1-2 frases",
    "sugestao_nome": "sugestao de nome da marca baseado no visual"
}"""

        # Montar parts com imagens (max 5)
        parts = []
        for img_b64 in imagens_b64[:5]:
            # Limpar prefixo data:image se existir
            clean = img_b64.split(",")[-1] if "," in img_b64 else img_b64
            parts.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": clean,
                }
            })
        parts.append({"text": prompt})

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json",
            },
        }

        model = "gemini-2.0-flash"
        url = GEMINI_API_URL.format(model=model)

        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(
                url,
                json=payload,
                headers={"x-goog-api-key": api_key},
            )
            res.raise_for_status()
            data = res.json()

        # Extrair texto da resposta
        text = ""
        for candidate in data.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if "text" in part:
                    text += part["text"]

        # Limpar possiveis markdown code blocks
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        return json.loads(text)
