"""Agregador de DNA da brand.

Cruza as analises individuais (analise_visual) de TODAS as refs da brand pra
extrair o DNA comum — traços que aparecem na maioria. Resultado: o "humano da
marca", nao um clone de uma ref especifica nem um cavalo marinho aleatorio.

Fluxo:
1. obter_ou_analisar pra cada ref (lazy — usa cache se ja analisado)
2. junta as analises individuais
3. manda pro Gemini agregar (pq Claude pode estar fora)
4. salva em brand.dna_agregado no Mongo

Output JSON:
{
  "constantes": {
    "paleta": ["#hex", ...],          // cores que se repetem
    "tipografia": "...",
    "tom_cores": "vibrante|pastel|...",
    "elementos_recorrentes": ["..."],
    "estilo_geral": "..."
  },
  "variaveis_livres": {
    "fundo": ["...", "..."],          // o que muda entre refs
    "composicao": ["..."],
    "outros": ["..."]
  },
  "n_refs_analisadas": int,
  "_meta": {"provider": "gemini", "atualizado_em": ISO8601}
}
"""

from __future__ import annotations

import json as _json
import os
from datetime import datetime, timezone

import httpx

from data.connections.mongo_connection import get_mongo_db
from services.ref_analyzer_service import obter_ou_analisar


GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)


AGGREGATE_PROMPT = """Voce vai receber N analises visuais de imagens de referencia da MESMA brand.
Essas refs sao exemplos do estilo da marca — algumas variam entre si, outras se repetem.

Sua tarefa: extrair o DNA da marca em duas partes:

1. CONSTANTES — traços que aparecem na maioria (>= 60%) das refs. Sao a "identidade".
2. VARIAVEIS LIVRES — o que muda entre as refs. Sao "espaco criativo" pra novas geracoes.

REGRAS CRITICAS:
- NAO invente elementos que nao estao nas analises (ex: nao adicione "astronauta" se nenhuma analise menciona).
- Cores: use HEX que aparecem em pelo menos 2 refs.
- Tom: pegue o mais comum (vibrante, pastel, neutro, etc).
- Se uma ref menciona elemento unico (ex: 1 tem astronauta), classifique como VARIAVEL, nao constante.

Retorne APENAS JSON valido com este schema:
{
  "constantes": {
    "paleta": ["#RRGGBB", ...],
    "tipografia": "descricao curta",
    "tom_cores": "vibrante|pastel|neutro|alto_contraste|escuro",
    "elementos_recorrentes": ["item1", "item2"],
    "estilo_geral": "descricao 1 frase do estilo da marca"
  },
  "variaveis_livres": {
    "fundo": ["fundo_ref_1", "fundo_ref_2"],
    "composicao": ["layout_ref_1", "layout_ref_2"],
    "outros": []
  }
}

Analises das refs:
"""


async def gerar_dna_agregado(
    brand_slug: str,
    claude_api_key: str = "",
    gemini_api_key: str = "",
) -> dict | None:
    """Agrega as analises individuais das refs em um DNA comum da brand.

    Salva o resultado em brand.dna_agregado no Mongo.
    Retorna o DNA agregado, ou None se falhar.
    """
    db = get_mongo_db()
    if db is None:
        return None

    # Pega todas as refs (com_avatar + sem_avatar) da brand
    refs_docs = list(db.brand_assets.find({
        "slug": brand_slug,
        "is_referencia": True,
    }))
    if not refs_docs:
        print(f"[dna_aggregator] brand '{brand_slug}' sem refs")
        return None

    if not gemini_api_key:
        gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    # Garante analise_visual em todas (lazy — usa cache se ja tem)
    analises = []
    for d in refs_docs:
        nome = d["nome"]
        analise = await obter_ou_analisar(brand_slug, nome, claude_api_key, gemini_api_key)
        if analise:
            analises.append({"ref_nome": nome, "analise": analise})
        else:
            print(f"[dna_aggregator] falha ao analisar ref {nome} — pulando")

    if not analises:
        print(f"[dna_aggregator] nenhuma analise obtida pra brand {brand_slug}")
        return None

    # Manda pro Gemini agregar
    dna_agregado = await _agregar_via_gemini(analises, gemini_api_key)
    if not dna_agregado:
        return None

    dna_agregado["n_refs_analisadas"] = len(analises)
    dna_agregado["_meta"] = {
        "provider": "gemini",
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
        "refs_usadas": [a["ref_nome"] for a in analises],
    }

    # Salva no doc da brand
    db.brands.update_one(
        {"slug": brand_slug},
        {"$set": {"dna_agregado": dna_agregado}},
    )
    return dna_agregado


async def _agregar_via_gemini(analises: list[dict], api_key: str) -> dict | None:
    """Chama Gemini com as N analises e pede o DNA agregado."""
    if not api_key or not analises:
        return None

    analises_json = _json.dumps(analises, ensure_ascii=False, indent=2)
    prompt = AGGREGATE_PROMPT + analises_json

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(GEMINI_URL, json=body, headers={"x-goog-api-key": api_key})
        if resp.status_code != 200:
            print(f"[dna_aggregator] Gemini HTTP {resp.status_code}: {resp.text[:200]}")
            return None
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return _parse_json_seguro(text)
    except Exception as e:
        print(f"[dna_aggregator] erro Gemini: {e}")
        return None


def _parse_json_seguro(raw: str) -> dict | None:
    if not raw:
        return None
    try:
        return _json.loads(raw)
    except (ValueError, TypeError):
        pass
    import re
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        try:
            return _json.loads(m.group(0))
        except (ValueError, TypeError):
            pass
    return None
