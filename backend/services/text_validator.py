"""Valida texto nas imagens geradas usando visao (Gemini).

Pos-producao: le o texto da imagem e compara com o esperado.
Se tiver erro significativo, marca pra regenerar.
"""
import json
import os

import httpx

from utils.constants import GEMINI_API_URL
API_URL = GEMINI_API_URL.format(model="gemini-2.0-flash")


async def validar_texto_slide(
    image_b64: str,
    texto_esperado: dict,
    gemini_api_key: str = "",
) -> dict:
    """Usa Gemini Vision pra ler texto da imagem e comparar com esperado.

    Args:
        image_b64: imagem em base64
        texto_esperado: dict com campos do slide (titulo, bullets, etc)
        gemini_api_key: chave da API

    Returns:
        dict com {valido: bool, erros: list[str], texto_lido: str}
    """
    if not gemini_api_key:
        gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    # Montar texto esperado como string
    partes = []
    if texto_esperado.get("titulo"):
        partes.append(texto_esperado["titulo"])
    if texto_esperado.get("headline"):
        partes.append(texto_esperado["headline"])
    if texto_esperado.get("corpo"):
        partes.append(texto_esperado["corpo"])
    if texto_esperado.get("subline"):
        partes.append(texto_esperado["subline"])
    for b in texto_esperado.get("bullets", []):
        partes.append(b)
    esperado = "\n".join(partes)

    # Preparar imagem
    raw = image_b64.split(",")[1] if "," in image_b64 else image_b64

    prompt = (
        "Leia TODO o texto visivel nesta imagem. "
        "Compare com o texto esperado abaixo e liste APENAS os erros de ortografia, "
        "palavras trocadas ou texto faltando. "
        "Se o texto estiver correto ou com diferenca minima (acentos), responda valido=true.\n\n"
        f"TEXTO ESPERADO:\n{esperado}\n\n"
        "Responda em JSON: {\"valido\": true/false, \"erros\": [\"descricao do erro\"], \"texto_lido\": \"texto que voce leu\"}"
    )

    payload = {
        "contents": [{
            "parts": [
                {"inline_data": {"mime_type": "image/png", "data": raw}},
                {"text": prompt},
            ]
        }],
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            res = await client.post(
                API_URL,
                json=payload,
                headers={"x-goog-api-key": gemini_api_key},
            )
            res.raise_for_status()
            data = res.json()

            # Extrair texto da resposta
            text = ""
            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "text" in part:
                        text += part["text"]

            # Parse JSON
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > 0:
                result = json.loads(text[start:end])
                return result

            return {"valido": True, "erros": [], "texto_lido": text}

        except Exception as e:
            # Se falhar a validacao, assume valido pra nao bloquear
            return {"valido": True, "erros": [f"Erro na validacao: {str(e)}"], "texto_lido": ""}


async def validar_e_regenerar(
    slides: list[dict],
    images: list[str | None],
    gerar_fn,
    gemini_api_key: str = "",
    max_tentativas: int = 2,
) -> list[str | None]:
    """Valida texto de cada slide e regenera os que tiverem erro.

    Args:
        slides: lista de dicts com dados dos slides
        images: lista de base64 das imagens geradas
        gerar_fn: funcao async que regenera 1 slide (recebe slide, index, total)
        gemini_api_key: chave
        max_tentativas: quantas vezes tentar regenerar

    Returns:
        lista de imagens (possivelmente corrigidas)
    """
    import asyncio

    resultado = list(images)

    for i, (slide, img) in enumerate(zip(slides, images)):
        if not img:
            continue

        for tentativa in range(max_tentativas):
            validacao = await validar_texto_slide(img, slide, gemini_api_key)

            if validacao.get("valido", True):
                break

            erros = validacao.get("erros", [])
            try:
                print(f"  Slide {i+1}: texto com erros. Regenerando (tentativa {tentativa+1})...")
            except UnicodeEncodeError:
                pass

            nova_img = await gerar_fn(slide, i, len(slides))
            if nova_img:
                resultado[i] = nova_img
                img = nova_img  # Validar a nova imagem no proximo loop
            else:
                break  # Nao conseguiu regenerar

            await asyncio.sleep(2)

    return resultado
