"""Analise visual pre-computada de refs de marca (Claude Vision).

Padrao "analyze-once, use-forever":
- Cada ref e analisada UMA vez via Claude Sonnet (vision)
- O resultado (composicao + paleta + blocos_conteudo + tipo_estrutural) fica
  salvo no campo analise_visual do doc em brand_assets.
- Usos subsequentes (art_director, image_generator) leem a analise textual
  direto do Mongo — sem custo extra de LLM.

Fluxo principal: obter_ou_analisar(brand_slug, ref_nome, api_key)
- Se doc.analise_visual existe -> retorna
- Se nao existe -> chama Claude Vision, salva, retorna
"""

from __future__ import annotations

import json as _json
import re
from typing import Any

from data.connections.mongo_connection import get_mongo_db


ANALYSIS_PROMPT = """Analise esta imagem de referencia visual de uma marca e descreva com precisao sua estrutura e estilo.

Retorne APENAS um JSON valido com este schema exato:

{
  "composicao": "descricao densa da estrutura visual em 1-3 frases — onde ficam cards, badges, logos, textos, setas; que parte do slide cada elemento ocupa. Seja ESPECIFICO.",
  "paleta": {
    "fundo": "#RRGGBB",
    "caixa_1": "#RRGGBB ou null",
    "caixa_2": "#RRGGBB ou null",
    "caixa_3": "#RRGGBB ou null",
    "texto_principal": "#RRGGBB",
    "acento": "#RRGGBB ou null"
  },
  "blocos_conteudo": <int: quantos blocos distintos de texto/card a composicao comporta>,
  "tipo_estrutural": "um de: capa_impacto | slide_bullets | slide_card_topo | comparativo | codigo | outro",
  "tom_cores": "vibrante | neutro_pastel | alto_contraste | escuro",
  "tem_seta_navegacao": true
}

Regras:
- PRESERVE a sutileza das cores: se uma caixa e lavanda MUITO palido quase-neutro, reporte como tal (#E8E2F5), nao como roxo vibrante (#9C27B0).
- Se um campo nao se aplica (ex: so tem 1 caixa), use null nos campos extras.
- JSON valido, sem comentarios, sem trailing commas.
"""


async def obter_ou_analisar(
    brand_slug: str,
    ref_nome: str,
    claude_api_key: str,
    gemini_api_key: str = "",
) -> dict | None:
    """Retorna a analise visual da ref. Analisa via Claude (fallback Gemini) se nao tiver cache.

    Retorna None se: Mongo indisponivel, ref nao encontrada, ou ambos LLMs falharam.
    """
    db = get_mongo_db()
    if db is None:
        return None

    doc = db.brand_assets.find_one({"slug": brand_slug, "nome": ref_nome})
    if not doc:
        return None

    cached = doc.get("analise_visual")
    if cached:
        return cached

    data_uri = doc.get("data_uri") or ""
    if not data_uri:
        return None

    b64 = data_uri.split(",", 1)[1] if "," in data_uri else data_uri
    media_type = "image/jpeg"
    if "image/png" in data_uri:
        media_type = "image/png"
    elif "image/webp" in data_uri:
        media_type = "image/webp"

    # Tenta Claude primeiro; se falhar (sem credito, etc), cai pro Gemini.
    analise = await _analisar_com_claude(b64, media_type, claude_api_key) if claude_api_key else None
    if not analise:
        if not gemini_api_key:
            import os
            gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        if gemini_api_key:
            print(f"[ref_analyzer] Claude indisponivel, fallback pro Gemini Vision")
            analise = await _analisar_com_gemini(b64, media_type, gemini_api_key)

    if not analise:
        return None

    try:
        db.brand_assets.update_one(
            {"_id": doc["_id"]},
            {"$set": {"analise_visual": analise}},
        )
    except Exception as e:
        print(f"[ref_analyzer] falha ao salvar analise de {brand_slug}/{ref_nome}: {e}")

    return analise


async def _analisar_com_claude(
    img_b64: str,
    media_type: str,
    api_key: str,
) -> dict | None:
    """Chama Claude Sonnet com vision pra analisar a ref. Retorna dict parseado."""
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=api_key)
        message = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": img_b64,
                        },
                    },
                    {"type": "text", "text": ANALYSIS_PROMPT},
                ],
            }],
        )
        raw = message.content[0].text
        return _parse_json_seguro(raw)
    except Exception as e:
        print(f"[ref_analyzer] Claude falhou: {e}")
        return None


async def _analisar_com_gemini(img_b64: str, media_type: str, api_key: str) -> dict | None:
    """Fallback: usa Gemini Vision (gemini-2.5-flash) pra analisar a ref."""
    if not api_key:
        return None
    try:
        import httpx
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-2.5-flash:generateContent"
        )
        body = {
            "contents": [{
                "parts": [
                    {"inline_data": {"mime_type": media_type, "data": img_b64}},
                    {"text": ANALYSIS_PROMPT},
                ],
            }],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json",
            },
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=body, headers={"x-goog-api-key": api_key})
        if resp.status_code != 200:
            print(f"[ref_analyzer Gemini] HTTP {resp.status_code}: {resp.text[:200]}")
            return None
        data = resp.json()
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            print(f"[ref_analyzer Gemini] resposta inesperada: {data}")
            return None
        return _parse_json_seguro(text)
    except Exception as e:
        print(f"[ref_analyzer Gemini] erro: {e}")
        return None


def _parse_json_seguro(raw: str) -> dict | None:
    """Extrai o primeiro JSON da resposta. Tolera texto envolvente."""
    if not raw:
        return None
    try:
        return _json.loads(raw)
    except (ValueError, TypeError):
        pass
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return None
    try:
        return _json.loads(m.group(0))
    except (ValueError, TypeError):
        return None


def invalidar_cache_analise(brand_slug: str, ref_nome: str) -> bool:
    """Remove a analise_visual do doc — forca re-analise no proximo uso.
    Util quando uma ref e substituida ou queremos refinar."""
    db = get_mongo_db()
    if db is None:
        return False
    result = db.brand_assets.update_one(
        {"slug": brand_slug, "nome": ref_nome},
        {"$unset": {"analise_visual": ""}},
    )
    return result.modified_count > 0
