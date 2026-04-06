import time
import json
from pathlib import Path

import httpx

CONFIGS_PATH = Path(__file__).parent.parent / "configs"
CACHE_PATH = Path(__file__).parent.parent / ".cache"
CACHE_TTL = 3600  # 1 hora


async def buscar_tendencias() -> list[dict]:
    """Busca tendencias dos criadores registrados.
    Cache de 1 hora.

    Retorna: lista de tendencias [{titulo, fonte, url, data}]
    """
    cached = _ler_cache()
    if cached:
        return cached

    tendencias = []

    # Dev.to
    try:
        tendencias.extend(await _buscar_devto())
    except Exception:
        pass

    # Hacker News
    try:
        tendencias.extend(await _buscar_hackernews())
    except Exception:
        pass

    _salvar_cache(tendencias)
    return tendencias


async def _buscar_devto() -> list[dict]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get("https://dev.to/api/articles?tag=ai&top=7&per_page=5")
        res.raise_for_status()
        return [
            {
                "titulo": a["title"],
                "fonte": "dev.to",
                "url": a["url"],
                "data": a["published_at"],
            }
            for a in res.json()
        ]


async def _buscar_hackernews() -> list[dict]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get("https://hacker-news.firebaseio.com/v0/topstories.json")
        res.raise_for_status()
        ids = res.json()[:5]
        items = []
        for story_id in ids:
            r = await client.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
            item = r.json()
            if item:
                items.append({
                    "titulo": item.get("title", ""),
                    "fonte": "hackernews",
                    "url": item.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                    "data": None,
                })
        return items


def _ler_cache() -> list[dict] | None:
    path = CACHE_PATH / "tendencias.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if time.time() - data.get("timestamp", 0) > CACHE_TTL:
        return None
    return data.get("items", [])


def _salvar_cache(items: list[dict]):
    CACHE_PATH.mkdir(exist_ok=True)
    path = CACHE_PATH / "tendencias.json"
    data = {"timestamp": time.time(), "items": items}
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
