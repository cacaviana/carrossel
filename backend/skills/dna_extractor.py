"""Skill de extracao de padrao visual — analisa multiplas refs e extrai a identidade recorrente.

Gera DOIS blocos:
1. dna: 4 strings curtas (backcompat com composicao do prompt)
2. padrao_visual: campos ricos que guiam o art_director (tipo_foto, composicoes,
   fundo_cenario, iluminacao, mood, elementos_overlay, relacao_pessoa_fundo, paleta)

IMPORTANTE: analisa MULTIPLAS imagens juntas pra extrair o padrao COMUM — nao
cores pontuais de uma foto isolada. So registra o que se repete em 2+ refs.
"""

import json

import httpx

from utils.constants import GEMINI_API_URL


_PROMPT_MULTI = """Voce analisa {n} imagens de referencia de uma mesma marca e extrai o PADRAO VISUAL recorrente — os elementos que se repetem e definem COMO a marca compoe suas imagens.

NAO descreva uma imagem especifica — descreva o PADRAO RECORRENTE.
Se duas imagens usam estruturas diferentes (ex: uma com pessoa em primeiro plano e outra com foto borrada como fundo), REGISTRE as DUAS no array de composicoes.

Responda APENAS em JSON valido com estes campos:

{{
  "dna": {{
    "estilo": "estilo COMUM entre as imagens em 3-6 palavras (ex: cute clean moderno)",
    "cores": "3-5 cores que se repetem nas imagens em 3-6 palavras (ex: rosa pastel, branco, bege)",
    "tipografia": "tipo de fonte comum em 3-6 palavras (ex: bold arredondada fofa)",
    "elementos": "elementos decorativos recorrentes em 3-6 palavras (ex: doodles leves, stickers)"
  }},
  "padrao_visual": {{
    "tipo_foto": "tipo de foto COMUM (ex: 'fotorealista editorial feminina', 'foto tech com pessoa interagindo', 'foto lifestyle natural'). Sempre foto real, nunca ilustracao/cartoon mesmo se parecer — isso eh overlay por cima da foto.",
    "composicoes": [
      "cada item descreve UMA estrutura recorrente de composicao em 1-2 frases curtas. Ex: 'pessoa em primeiro plano olhando pra camera com cenario simples atras'. Se a marca usa 2 estruturas diferentes, liste as 2. MINIMO 1, MAXIMO 3."
    ],
    "fundo_cenario": "o que geralmente aparece atras da pessoa ou como fundo (ex: 'paredes claras creme, sem distracao', 'escritorio tech com luzes neon roxas', 'natureza verde desfocada')",
    "iluminacao": "tipo de luz predominante (ex: 'natural suave tom quente', 'neon roxo frio', 'dourada editorial')",
    "mood": "vibe/sensacao que as imagens transmitem (ex: 'aconchegante feminino proximo', 'autoridade tech futurista', 'relaxado natural')",
    "elementos_overlay": "o que aparece POR CIMA da foto como overlay (ex: 'titulo 3D inflado pastel + doodles fofos', 'texto neon brilhante + linhas de grid', 'nenhum overlay, foto limpa')",
    "paleta_dominante": ["lista de 3-5 cores em hex que aparecem consistentemente, ex: #FDFBF8"],
    "relacao_pessoa_fundo": "como pessoa se relaciona com o fundo (ex: 'pessoa domina primeiro plano, fundo suporta', 'pessoa integrada com elementos tech', 'fundo borrado, pessoa nao aparece')"
  }}
}}

REGRAS:
- So inclui o que aparece em 2+ imagens (padrao real)
- Se a marca tem so 1 ref, baseia o padrao_visual nessa ref, mas reconhece a limitacao
- composicoes eh ARRAY — se ve variacoes, registra as variacoes
- Sem markdown, sem texto fora do JSON, APENAS o JSON
"""


def _detect_mime(raw_b64: str) -> str:
    """Detecta mime a partir dos primeiros bytes do base64."""
    if raw_b64.startswith("/9j/"):
        return "image/jpeg"
    if raw_b64.startswith("iVBOR"):
        return "image/png"
    if raw_b64.startswith("UklGR"):
        return "image/webp"
    return "image/jpeg"


def _trim(val: str, max_words: int = 6) -> str:
    words = str(val or "").strip().split()
    return " ".join(words[:max_words])


async def extrair_dna(imagens_b64: list[str], api_key: str) -> dict:
    """Extrai DNA curto + padrao_visual rico a partir de multiplas refs.

    Args:
        imagens_b64: lista de imagens em base64 (com ou sem data URI prefix).
                     Analise agregada pra extrair o padrao REAL da marca.
        api_key: Gemini API key

    Returns:
        dict com chaves 'estilo', 'cores', 'tipografia', 'elementos' (backcompat)
        + 'padrao_visual' com os campos ricos.

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

    async with httpx.AsyncClient(timeout=120.0) as client:
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

    # Extrair DNA curto (backcompat com prompt composer)
    dna_raw = result.get("dna", {}) if isinstance(result, dict) else {}
    dna = {
        "estilo": _trim(dna_raw.get("estilo", "")),
        "cores": _trim(dna_raw.get("cores", "")),
        "tipografia": _trim(dna_raw.get("tipografia", "")),
        "elementos": _trim(dna_raw.get("elementos", "")),
    }

    # Padrao visual rico (campos novos que alimentam o art_director)
    padrao = result.get("padrao_visual", {}) if isinstance(result, dict) else {}
    if isinstance(padrao, dict):
        composicoes = padrao.get("composicoes") or []
        if not isinstance(composicoes, list):
            composicoes = [str(composicoes)]
        paleta = padrao.get("paleta_dominante") or []
        if not isinstance(paleta, list):
            paleta = []
        dna["padrao_visual"] = {
            "tipo_foto": str(padrao.get("tipo_foto", "")).strip(),
            "composicoes": [str(c).strip() for c in composicoes if str(c).strip()][:3],
            "fundo_cenario": str(padrao.get("fundo_cenario", "")).strip(),
            "iluminacao": str(padrao.get("iluminacao", "")).strip(),
            "mood": str(padrao.get("mood", "")).strip(),
            "elementos_overlay": str(padrao.get("elementos_overlay", "")).strip(),
            "paleta_dominante": [str(c).strip() for c in paleta if str(c).strip()][:5],
            "relacao_pessoa_fundo": str(padrao.get("relacao_pessoa_fundo", "")).strip(),
        }

    return dna
