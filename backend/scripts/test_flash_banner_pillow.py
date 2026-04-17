"""Teste: Gemini Flash faz foto+banner, Pillow adiciona texto. Topo e baixo."""
import asyncio
import base64
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
load_dotenv(BACKEND_DIR / ".env")

from services.smart_image_service import _gerar_criativo_flash_plus_pillow
from services.brand_prompt_builder import carregar_brand


async def gerar(posicao: str, photo_b64: str, gemini_key: str, cor_hero: str, banner_desc: str | None) -> Path:
    async with httpx.AsyncClient(timeout=300.0) as client:
        result = await _gerar_criativo_flash_plus_pillow(
            client=client,
            headline="A IA vai te substituir",
            background_b64=photo_b64,
            gemini_key=gemini_key,
            formato="capa_reels",
            cor_hero=cor_hero,
            posicao=posicao,
            banner_descricao=banner_desc,
        )

    if not result:
        raise RuntimeError(f"no image for {posicao}")

    raw = result.split(",", 1)[1] if "," in result else result
    out = BACKEND_DIR / "scripts" / f"test_flash_banner_{posicao}.png"
    out.write_bytes(base64.b64decode(raw))
    return out


async def main():
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    assert gemini_key, "GEMINI_API_KEY missing"

    photo_path = BACKEND_DIR / "assets" / "pipeline-images" / "b8779a0c-4964-47aa-91fa-7048689e8417" / "slide-00.png"
    photo_bytes = photo_path.read_bytes()
    photo_b64 = f"data:image/png;base64,{base64.b64encode(photo_bytes).decode()}"

    brand = carregar_brand("itvalley") or {}
    print(f"brand keys: {list(brand.keys())}")
    print(f"dna keys: {list((brand.get('dna') or {}).keys())}")
    cor_hero = (brand.get("cores") or {}).get("acento_principal") or "#A78BFA"
    banner_desc = ((brand.get("dna") or {}).get("banner")) or None

    print(f"cor_hero: {cor_hero}")
    print(f"banner_desc: {(banner_desc or '(default)')[:80]}...")

    top_path, bottom_path = await asyncio.gather(
        gerar("topo", photo_b64, gemini_key, cor_hero, banner_desc),
        gerar("baixo", photo_b64, gemini_key, cor_hero, banner_desc),
    )
    print(f"[ok] topo  -> {top_path}")
    print(f"[ok] baixo -> {bottom_path}")


if __name__ == "__main__":
    asyncio.run(main())
