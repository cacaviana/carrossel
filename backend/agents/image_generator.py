import os
import asyncio
import logging

import httpx

from skills.variation_engine import gerar_variacoes
from mappers.imagem_mapper import extract_image_from_response

from utils.constants import GEMINI_API_URL as API_URL
FALLBACK_MODEL = "gemini-2.5-flash-image"
MAX_RETRIES = 2
MAX_CONCURRENT_IMAGES = 3  # Gemini rate limit safe

logger = logging.getLogger(__name__)


async def executar(
    prompts: list[dict],
    formato: str,
    gemini_api_key: str = "",
    step_id: str = "",
) -> dict:
    """Executa o Image Generator: gera 3 variacoes de imagem por slide via Gemini API.
    Usa Pro para capa/CTA, Flash para o resto. Retry com fallback para Flash.

    Usa asyncio.gather com semaforo para paralelizar chamadas ao Gemini,
    limitando a MAX_CONCURRENT_IMAGES simultaneas pra respeitar rate limit.
    """
    from services.step_progress import atualizar as progress_update, limpar as progress_clear

    if not gemini_api_key:
        gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    total = len(prompts)
    total_imagens = total * 3  # 3 variacoes por slide
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_IMAGES)
    progress_lock = asyncio.Lock()
    geradas_counter = {"value": 0}

    # Preparar todas as tarefas (slide x variacao)
    async def process_variation(
        slide_index: int, var_num: int, prompt_variacao: str, modelo: str,
        order_key: tuple[int, int],
    ) -> tuple[tuple[int, int], dict]:
        async with semaphore:
            if step_id:
                async with progress_lock:
                    progress_update(step_id, geradas_counter["value"], total_imagens, f"Slide {slide_index} var {var_num}")
            async with httpx.AsyncClient(timeout=120.0) as client:
                result = await _gerar_com_retry(
                    client, prompt_variacao, modelo, gemini_api_key,
                    slide_index, var_num,
                )
            if step_id:
                async with progress_lock:
                    geradas_counter["value"] += 1
                    progress_update(step_id, geradas_counter["value"], total_imagens, f"Slide {slide_index} var {var_num}")
            return (order_key, result)

    tasks = []
    for idx, prompt_item in enumerate(prompts):
        slide_index = prompt_item.get("slide_index") or prompt_item.get("slide", idx + 1)
        prompt_base = prompt_item.get("prompt", "")
        variacoes = gerar_variacoes(prompt_base)

        for var_num, prompt_variacao in enumerate(variacoes, start=1):
            modelo = _select_model(slide_index, total)
            tasks.append(process_variation(
                slide_index, var_num, prompt_variacao, modelo,
                order_key=(idx, var_num),
            ))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Ordenar por (idx, var_num) pra manter a ordem original
    ordered: list[tuple[tuple[int, int], dict]] = []
    for r in results:
        if isinstance(r, Exception):
            logger.error("Tarefa de geracao falhou: %s", r)
            continue
        ordered.append(r)
    ordered.sort(key=lambda x: x[0])
    imagens = [item[1] for item in ordered]

    if step_id:
        progress_clear(step_id)

    return {"imagens": imagens}


async def _gerar_com_retry(
    client: httpx.AsyncClient,
    prompt: str,
    modelo: str,
    api_key: str,
    slide_index: int,
    var_num: int,
) -> dict:
    """Tenta gerar imagem com retry. Se Pro falha, faz fallback para Flash."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
    }

    modelos_tentar = [modelo]
    if modelo != FALLBACK_MODEL:
        modelos_tentar.append(FALLBACK_MODEL)

    last_error = None
    for modelo_atual in modelos_tentar:
        for attempt in range(MAX_RETRIES):
            try:
                res = await client.post(
                    API_URL.format(model=modelo_atual),
                    json=payload,
                    headers={"x-goog-api-key": api_key},
                )
                res.raise_for_status()
                image_b64 = extract_image_from_response(res.json())

                return {
                    "slide_index": slide_index,
                    "variacao": var_num,
                    "image_base64": image_b64,
                    "modelo": modelo_atual,
                }
            except Exception as e:
                last_error = e
                logger.warning(
                    "Slide %d var %d: %s attempt %d falhou: %s",
                    slide_index, var_num, modelo_atual, attempt + 1, e,
                )
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(3 * (attempt + 1))

    return {
        "slide_index": slide_index,
        "variacao": var_num,
        "image_base64": None,
        "modelo": modelo,
        "erro": str(last_error),
    }


def _select_model(slide_index: int, total_slides: int) -> str:
    """Pro para todos os slides — qualidade consistente."""
    return "gemini-3-pro-image-preview"


# Formato 'anuncio' (pos-pivot 2026-04-23):
# Anuncio e 1 formato 1080x1350 com mesma dimensao do post_unico.
# Nao ha logica de multi-dimensao -- usa o mesmo caminho de geracao
# via imagem_service/pipeline_executor com formato="anuncio".
