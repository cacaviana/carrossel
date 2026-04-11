"""Skill de extracao de DNA visual — 4 linhas curtas que definem a identidade.

Diferente do visual_extractor (que extrai TUDO em dezenas de campos), esse aqui
devolve so 4 strings curtas: estilo, cores, tipografia, elementos. Feito pra
alimentar o bloco [DNA] do prompt composer (Fase 0).
"""

import json
import httpx
from utils.constants import GEMINI_API_URL


_PROMPT = """Voce analisa uma imagem de referencia visual e extrai 4 linhas CURTAS que definem o DNA visual da marca.

Responda em JSON valido com APENAS estes 4 campos, cada um com 3-6 palavras em portugues:

{
    "estilo": "palavras-chave do estilo (ex: cute clean moderno)",
    "cores": "3-5 cores principais (ex: rosa pastel, branco, dourado)",
    "tipografia": "tipo de fonte (ex: bold arredondada fofa)",
    "elementos": "elementos decorativos (ex: doodles leves, stickers)"
}

REGRAS:
- Maximo 6 palavras por campo
- Sem narrativa, sem explicacao
- APENAS o JSON, sem markdown, sem texto fora do JSON
"""


async def extrair_dna(imagem_b64: str, api_key: str) -> dict:
    """Extrai DNA visual (4 linhas) de uma imagem de referencia.

    Args:
        imagem_b64: imagem em base64 (com ou sem data URI prefix)
        api_key: Gemini API key

    Returns:
        dict com chaves 'estilo', 'cores', 'tipografia', 'elementos'

    Raises:
        httpx.HTTPError: se a API falhou
        json.JSONDecodeError: se a resposta nao eh JSON valido
    """
    clean = imagem_b64.split(",")[-1] if "," in imagem_b64 else imagem_b64

    payload = {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": "image/png", "data": clean}},
            {"text": _PROMPT},
        ]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }

    model = "gemini-2.5-flash"
    url = GEMINI_API_URL.format(model=model)

    async with httpx.AsyncClient(timeout=60.0) as client:
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
