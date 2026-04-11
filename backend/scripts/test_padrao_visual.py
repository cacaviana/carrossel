"""Script standalone pra validar novo prompt Gemini expandido.

Roda o novo prompt nas refs ja salvas no Mongo da marca passada por arg.
Mostra JSON cru pra decidir se rolamos o refactor ou ajustamos o prompt.

Uso:
    python scripts/test_padrao_visual.py <slug> [pool]
    pool = com_avatar (default) | sem_avatar

Ex:
    python scripts/test_padrao_visual.py jennie com_avatar
    python scripts/test_padrao_visual.py jennie sem_avatar
"""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import httpx

from factories.imagem_factory import _load_references_by_pool
from utils.constants import GEMINI_API_URL


PROMPT_PADRAO_VISUAL = """Voce analisa {n} imagens de referencia de uma mesma marca e extrai o PADRAO VISUAL recorrente — os elementos que se repetem e definem COMO a marca compoe suas imagens.

NAO descreva uma imagem especifica — descreva o PADRAO RECORRENTE.
Se duas imagens usam estruturas diferentes (ex: uma com pessoa em primeiro plano e outra com foto borrada como fundo), REGISTRE as DUAS no array de composicoes.

Responda APENAS em JSON valido com estes campos:

{{
  "tipo_foto": "descreva o tipo de foto COMUM (ex: 'fotorealista editorial feminina', 'foto tech com pessoa interagindo', 'foto lifestyle natural'). Sempre foto real, nunca ilustracao/cartoon mesmo se parecer — isso eh overlay por cima da foto.",
  "composicoes": [
    "Cada item descreve UMA estrutura recorrente de composicao. Ex: 'pessoa em primeiro plano olhando pra camera com cenario simples atras'. Cada item 1-2 frases curtas. Se a marca usa 2 estruturas diferentes, liste as 2. MINIMO 1, MAXIMO 3."
  ],
  "fundo_cenario": "o que geralmente aparece ATRAS da pessoa ou como fundo (ex: 'paredes claras creme, sem distracao', 'escritorio tech com luzes neon roxas', 'natureza verde desfocada')",
  "iluminacao": "tipo de luz predominante (ex: 'natural suave tom quente', 'neon roxo frio', 'dourada editorial')",
  "mood": "vibe/sensacao que as imagens transmitem (ex: 'aconchegante feminino proximo', 'autoridade tech futurista', 'relaxado natural')",
  "elementos_overlay": "o que aparece POR CIMA da foto como overlay (ex: 'titulo 3D inflado pastel + doodles fofos', 'texto neon brilhante + linhas de grid', 'nenhum overlay, foto limpa')",
  "paleta_dominante": ["lista de 3-5 cores em hex que aparecem consistentemente, ex: #FDFBF8"],
  "relacao_pessoa_fundo": "como pessoa se relaciona com o fundo (ex: 'pessoa domina primeiro plano, fundo suporta', 'pessoa integrada com elementos tech', 'fundo borrado, pessoa nao aparece')"
}}

REGRAS:
- So inclui o que aparece em 2+ imagens (padrao real)
- SEMPRE tipo_foto em portugues, descritivo
- composicoes eh ARRAY — se ve variacoes, registra as variacoes
- Sem markdown, sem texto fora do JSON, APENAS o JSON
"""


def _detect_mime(raw_b64: str) -> str:
    if raw_b64.startswith("/9j/"):
        return "image/jpeg"
    if raw_b64.startswith("iVBOR"):
        return "image/png"
    if raw_b64.startswith("UklGR"):
        return "image/webp"
    return "image/jpeg"


async def extrair_padrao(imagens_b64: list[str], api_key: str) -> dict:
    if not imagens_b64:
        raise ValueError("Sem imagens")

    imagens_b64 = imagens_b64[:5]

    parts = []
    for img in imagens_b64:
        clean = img.split(",")[-1] if "," in img else img
        parts.append({"inline_data": {"mime_type": _detect_mime(clean), "data": clean}})

    parts.append({"text": PROMPT_PADRAO_VISUAL.format(n=len(imagens_b64))})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }

    url = GEMINI_API_URL.format(model="gemini-2.5-flash")
    async with httpx.AsyncClient(timeout=120.0) as client:
        res = await client.post(url, json=payload, headers={"x-goog-api-key": api_key})
        res.raise_for_status()
        data = res.json()

    text = ""
    for cand in data.get("candidates", []):
        for p in cand.get("content", {}).get("parts", []):
            if "text" in p:
                text += p["text"]

    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    return json.loads(text.strip())


async def main():
    slug = sys.argv[1] if len(sys.argv) > 1 else "jennie"
    pool = sys.argv[2] if len(sys.argv) > 2 else "com_avatar"

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        print("ERRO: GEMINI_API_KEY nao configurada no .env")
        sys.exit(1)

    print(f"=== Carregando refs de {slug} pool={pool} ===")
    refs = _load_references_by_pool(slug, pool)
    print(f"Refs encontradas: {len(refs)}")
    if not refs:
        print(f"Nenhuma ref no pool {pool}. Tentando o outro pool...")
        outro = "sem_avatar" if pool == "com_avatar" else "com_avatar"
        refs = _load_references_by_pool(slug, outro)
        print(f"Refs no pool {outro}: {len(refs)}")
        pool = outro

    if not refs:
        print(f"ERRO: marca {slug} nao tem refs em nenhum pool")
        sys.exit(1)

    print(f"\n=== Rodando Gemini 2.5 Flash com {len(refs)} refs do pool {pool} ===")
    padrao = await extrair_padrao(refs, api_key)

    print(f"\n=== PADRAO VISUAL EXTRAIDO ({slug} / {pool}) ===")
    print(json.dumps(padrao, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
