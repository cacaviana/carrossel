"""Skill de extracao de DNA visual — 4 linhas curtas que definem a identidade.

Diferente do visual_extractor (que extrai TUDO em dezenas de campos), esse aqui
devolve so 4 strings curtas: estilo, cores, tipografia, elementos. Feito pra
alimentar o bloco [DNA] do prompt composer (Fase 0).

IMPORTANTE: analisa MULTIPLAS imagens juntas pra extrair o DNA COMUM da marca,
nao cores pontuais de uma unica foto. Isso reflete melhor a identidade real.
"""

import json
import httpx
from utils.constants import GEMINI_API_URL


_PROMPT_MULTI = """Voce analisa {n} imagens de referencia visual de uma mesma marca e extrai o DNA VISUAL COMUM entre elas — os elementos que se repetem e definem a identidade.

NAO descreva o que aparece em UMA imagem especifica — descreva o PADRAO que se repete em todas.
Se uma foto tem cores pontuais que nao aparecem nas outras, IGNORE — nao faz parte do DNA.

Responda em JSON valido com APENAS estes 4 campos, cada um com 3-6 palavras em portugues:

{{
    "estilo": "estilo COMUM entre as imagens (ex: cute clean moderno)",
    "cores": "3-5 cores que se REPETEM nas imagens (ex: rosa pastel, branco, bege)",
    "tipografia": "tipo de fonte COMUM (ex: bold arredondada fofa)",
    "elementos": "elementos decorativos RECORRENTES (ex: doodles leves, stickers)"
}}

REGRAS:
- Maximo 6 palavras por campo
- So inclui o que aparece em 2+ imagens
- Sem narrativa, sem explicacao
- APENAS o JSON, sem markdown, sem texto fora do JSON
"""


def _detect_mime(raw_b64: str) -> str:
    """Detecta mime a partir dos primeiros bytes do base64."""
    # PNG: iVBOR, JPEG: /9j/, WebP: UklGR
    if raw_b64.startswith("/9j/"):
        return "image/jpeg"
    if raw_b64.startswith("iVBOR"):
        return "image/png"
    if raw_b64.startswith("UklGR"):
        return "image/webp"
    return "image/jpeg"


async def extrair_dna(imagens_b64: list[str], api_key: str) -> dict:
    """Extrai DNA visual (4 linhas) comum a multiplas imagens de referencia.

    Args:
        imagens_b64: lista de imagens em base64 (com ou sem data URI prefix).
                     Analise agregada pra extrair o DNA REAL da marca, nao
                     cores pontuais de uma foto isolada.
        api_key: Gemini API key

    Returns:
        dict com chaves 'estilo', 'cores', 'tipografia', 'elementos'

    Raises:
        ValueError: se lista vazia
        httpx.HTTPError: se a API falhou
        json.JSONDecodeError: se a resposta nao eh JSON valido
    """
    if not imagens_b64:
        raise ValueError("Nenhuma imagem fornecida pra extrair DNA")

    # Limitar a 5 imagens pra caber no payload Gemini sem estourar
    imagens_b64 = imagens_b64[:5]

    parts: list[dict] = []
    for img in imagens_b64:
        clean = img.split(",")[-1] if "," in img else img
        parts.append({"inline_data": {"mime_type": _detect_mime(clean), "data": clean}})

    parts.append({"text": _PROMPT_MULTI.format(n=len(imagens_b64))})

    payload = {
        "contents": [{"parts": parts}],
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

    result = json.loads(text.strip())

    # Normalizar: garantir as 4 chaves, cortar em 6 palavras
    def _trim(val: str, max_words: int = 6) -> str:
        words = str(val or "").strip().split()
        return " ".join(words[:max_words])

    return {
        "estilo": _trim(result.get("estilo", "")),
        "cores": _trim(result.get("cores", "")),
        "tipografia": _trim(result.get("tipografia", "")),
        "elementos": _trim(result.get("elementos", "")),
    }
