"""Teste isolado do gpt-image-1 para modo criativo upload."""
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

from factories.imagem_factory import build_payload


async def main():
    openai_key = os.getenv("OPENAI_API_KEY", "")
    assert openai_key, "OPENAI_API_KEY missing"

    photo_path = BACKEND_DIR / "assets" / "pipeline-images" / "b8779a0c-4964-47aa-91fa-7048689e8417" / "slide-00.png"
    assert photo_path.exists(), f"{photo_path} not found"

    photo_bytes = photo_path.read_bytes()
    photo_b64 = f"data:image/png;base64,{base64.b64encode(photo_bytes).decode()}"

    slide = {
        "type": "capa",
        "position": 1,
        "headline": "A IA vai te substituir",
        "subline": "",
        "bullets": [],
        "illustration_description": "Editorial poster with creative visual elements and layers",
    }

    _, payload = build_payload(
        slide, 1, 1,
        brand_slug="itvalley",
        formato="capa_reels",
        avatar_mode="livre",
        background_b64=photo_b64,
    )

    prompt_text = ""
    for part in payload["contents"][0]["parts"]:
        if "text" in part:
            prompt_text = part["text"]
            break

    print(f"[prompt len] {len(prompt_text)} chars")
    print(f"[prompt preview]\n{prompt_text[:600]}...\n")

    async with httpx.AsyncClient(timeout=300.0) as client:
        res = await client.post(
            "https://api.openai.com/v1/images/edits",
            files={"image": ("photo.png", photo_bytes, "image/png")},
            data={
                "model": "gpt-image-1",
                "prompt": prompt_text[:32000],
                "n": "1",
                "size": "1024x1536",
                "quality": "high",
            },
            headers={"Authorization": f"Bearer {openai_key}"},
        )
        print(f"[http] {res.status_code}")
        if res.status_code != 200:
            print(res.text[:2000])
            return
        result = res.json()

    b64 = result["data"][0]["b64_json"]
    out = BACKEND_DIR / "scripts" / "test_openai_criativo_output.png"
    out.write_bytes(base64.b64decode(b64))
    print(f"[ok] saved {out}")


if __name__ == "__main__":
    asyncio.run(main())
