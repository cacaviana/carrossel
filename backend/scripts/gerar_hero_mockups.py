"""Gera 3 imagens de mockup para o hero da landing page via Gemini."""
import asyncio
import base64
import httpx
from pathlib import Path

import os
API_KEY = os.getenv("GEMINI_API_KEY", "")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "static"

DESIGN_SYSTEM = """
DESIGN SYSTEM — Dark Mode Premium
- Background: deep dark gradient #0A0A0F to #1a0a2e (NEVER pure black)
- Accent: #A78BFA (purple lilac) for keywords, highlights
- Secondary accents: #34D399 (green neon), #FBBF24 (amber)
- Text: #FFFFFF titles, #9896A3 body
- Font style: Outfit (clean, modern sans-serif)
- Borders: subtle 1px rgba(167,139,250,0.2)
- Cards: rounded corners (16px), subtle glow effects
- Atmosphere: cosmic, tech, premium, professional
- Format: 1080x1350 portrait (carousel slide for LinkedIn/Instagram)
- Badge pill at top with category
- Footer: small avatar circle + name "Carlos Viana" + page number
"""

SLIDES = [
    {
        "filename": "hero-mock-1.png",
        "prompt": f"""Create a stunning social media carousel COVER SLIDE image.

{DESIGN_SYSTEM}

CONTENT FOR THIS SLIDE:
- Title: "3 regras do conteudo viral" — large, bold, white text with "viral" highlighted in purple #A78BFA
- Style: modern tech/content creator aesthetic
- Include a cosmic/galaxy background with subtle purple nebula effects
- Add a small green badge pill at top: "CONTEUDO"
- Include abstract geometric elements (lines, dots, neural network patterns)
- Small footer: circle avatar placeholder + "Carlos Viana" + "01 / 07"
- The overall vibe should be: premium, dark, techy, aspirational
- DO NOT include any real photo of a person
- Text must be PERFECTLY legible and correctly spelled
"""
    },
    {
        "filename": "hero-mock-2.png",
        "prompt": f"""Create a stunning social media carousel COVER SLIDE image.

{DESIGN_SYSTEM}

CONTENT FOR THIS SLIDE:
- Title: "Depois que aprendi isso minha vida mudou" — large, emotional text, "minha vida mudou" in purple #A78BFA
- Style: wellness/self-improvement meets tech. Modern and warm but still dark mode
- Include a silhouette or abstract representation of a person meditating or looking at horizon
- Cosmic/galaxy background with warmer purple and subtle amber tones
- Add a small amber badge pill at top: "MINDSET"
- Small footer: circle avatar placeholder + "Carlos Viana" + "01 / 10"
- Vibe: introspective, premium, modern wellness-tech crossover
- DO NOT include any real photo, use artistic silhouette/illustration style
- Text must be PERFECTLY legible and correctly spelled
"""
    },
    {
        "filename": "hero-mock-3.png",
        "prompt": f"""Create a stunning social media carousel COVER SLIDE image.

{DESIGN_SYSTEM}

CONTENT FOR THIS SLIDE:
- Title: "Nao pule esse post" — large, bold, attention-grabbing. "esse post" in bright purple #A78BFA
- Style: urgent, curiosity-driven, stop-the-scroll
- Include a bold visual element: maybe a large hand gesture (stop/point), or a dramatic light beam
- Dark cosmic background with intense purple glow at center
- Add a small red badge pill at top: "ALERTA"
- Include a subtle arrow or visual cue suggesting "swipe"
- Small footer: circle avatar placeholder + "Carlos Viana" + "01 / 03"
- Vibe: dramatic, can't-miss, premium dark mode
- DO NOT include any real photo of a person
- Text must be PERFECTLY legible and correctly spelled
"""
    },
]


async def generate(slide: dict, client: httpx.AsyncClient) -> None:
    payload = {
        "contents": [{"parts": [{"text": slide["prompt"]}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "temperature": 0.9,
        },
    }
    print(f"Gerando {slide['filename']}...")
    res = await client.post(
        API_URL,
        json=payload,
        headers={"x-goog-api-key": API_KEY},
    )
    res.raise_for_status()
    data = res.json()

    # Extract image
    for candidate in data.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if "inlineData" in part:
                img_b64 = part["inlineData"]["data"]
                out = OUTPUT_DIR / slide["filename"]
                out.write_bytes(base64.b64decode(img_b64))
                print(f"  Salvo: {out}")
                return

    print(f"  ERRO: sem imagem na resposta de {slide['filename']}")


async def main():
    async with httpx.AsyncClient(timeout=120.0) as client:
        for slide in SLIDES:
            await generate(slide, client)
            await asyncio.sleep(2)  # rate limit

    print("\nDone! 3 mockups gerados em frontend/static/")


if __name__ == "__main__":
    asyncio.run(main())
