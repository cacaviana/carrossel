import os

from fastapi import APIRouter, Depends, HTTPException, Request

from dtos.imagem.gerar_imagem.request import GerarImagemRequest, GerarImagemSlideRequest
from dtos.imagem.gerar_imagem.response import GerarImagemResponse, GerarImagemSlideResponse
from middleware.auth import CurrentUser, get_current_user
from services.imagem_service import gerar_imagens, gerar_imagem_slide
from middleware.rate_limiter import limiter

router = APIRouter()


@router.post("/gerar-imagem", response_model=GerarImagemResponse)
@limiter.limit("5/minute")
async def api_gerar_imagem(
    request: Request,
    req: GerarImagemRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="GEMINI_API_KEY não configurada. Acesse /configuracoes.")
    try:
        slides_dicts = [s.model_dump() for s in req.slides]
        # Injetar instrucao_extra no primeiro slide (feedback do usuario)
        if req.instrucao_extra and slides_dicts:
            for sd in slides_dicts:
                sd["instrucao_extra"] = req.instrucao_extra
        brand = req.brand_slug
        if not brand:
            from services.brand_prompt_builder import listar_brands
            brands = listar_brands()
            brand = brands[0]["slug"] if brands else ""
        from services.smart_image_service import gerar_imagens_smart
        images = await gerar_imagens_smart(
            slides=slides_dicts,
            gemini_api_key=api_key,
            brand_slug=brand,
            formato=req.formato,
            skip_validation=req.skip_validation,
            avatar_mode=req.avatar_mode,
            pipeline_id=req.pipeline_id,
        )
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ajustar-imagem")
@limiter.limit("10/minute")
async def api_ajustar_imagem(
    request: Request,
    data: dict,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Recebe imagem existente + feedback e aplica ajuste minimo.
    Body: {imagem: base64, feedback: string, brand_slug?: string}"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="GEMINI_API_KEY nao configurada")
    imagem = data.get("imagem", "")
    feedback = data.get("feedback", "")
    brand_slug = data.get("brand_slug")
    if not imagem or not feedback:
        raise HTTPException(status_code=400, detail="Campos 'imagem' e 'feedback' obrigatorios")
    try:
        import httpx
        from utils.image_adjuster import ajustar_imagem
        from factories.imagem_factory import _load_all_references
        ref = None
        if brand_slug:
            refs = _load_all_references(brand_slug)
            if refs:
                import random
                ref = random.choice(refs)
        async with httpx.AsyncClient(timeout=120.0) as client:
            result = await ajustar_imagem(client, imagem, feedback, api_key, ref_image_b64=ref)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/corrigir-avatar")
@limiter.limit("10/minute")
async def api_corrigir_avatar(
    request: Request,
    data: dict,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Recebe imagem gerada + brand_slug, regenera com o avatar correto da marca.
    Body: {imagem: base64, brand_slug: string, pipeline_id?: string, slide_index?: int}"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="GEMINI_API_KEY nao configurada")

    imagem = data.get("imagem", "")
    brand_slug = data.get("brand_slug", "")
    pipeline_id = data.get("pipeline_id")
    slide_index = data.get("slide_index")

    if not imagem:
        raise HTTPException(status_code=400, detail="Campo 'imagem' obrigatorio")
    if not brand_slug:
        raise HTTPException(status_code=400, detail="Campo 'brand_slug' obrigatorio")

    try:
        from services.avatar_fixer import corrigir_avatar
        result_b64 = await corrigir_avatar(imagem, brand_slug, api_key)

        # Se veio pipeline_id + slide_index, salvar no disco
        if pipeline_id and slide_index:
            from utils.pipeline_images import salvar_imagem
            path_rel = salvar_imagem(pipeline_id, int(slide_index), result_b64)
            return {"image": result_b64, "image_path": path_rel}

        return {"image": result_b64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gerar-imagem-slide", response_model=GerarImagemSlideResponse)
@limiter.limit("5/minute")
async def api_gerar_imagem_slide(
    request: Request,
    req: GerarImagemSlideRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="GEMINI_API_KEY não configurada. Acesse /configuracoes.")
    try:
        image = await gerar_imagem_slide(
            slide=req.slide.model_dump(),
            slide_index=req.slide_index,
            total_slides=req.total_slides,
            gemini_api_key=api_key,
            foto_criador=req.foto_criador,
            design_system=req.design_system,
            reference_image=req.reference_image,
            formato=req.formato,
            brand_slug=req.brand_slug,
            avatar_mode=req.avatar_mode,
            pipeline_id=req.pipeline_id,
        )
        return {"image": image}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image-to-base64")
async def image_to_base64(
    data: dict,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Converte URL interna de imagem pra data URI base64 (leitura direta do disco)."""
    import base64, re
    from pathlib import Path

    url = data.get("url", "")
    if not url:
        raise HTTPException(status_code=400, detail="url obrigatoria")

    try:
        # Pipeline image: /api/pipelines/{id}/imagens/{index}
        m = re.search(r"/pipelines/([^/]+)/imagens/(\d+)", url)
        if m:
            pid, idx = m.group(1), int(m.group(2))
            from utils.pipeline_images import caminho_absoluto
            path = caminho_absoluto(f"pipeline-images/{pid}/slide-{idx:02d}.png")
            if path:
                b64 = base64.b64encode(Path(path).read_bytes()).decode()
                return {"data_uri": f"data:image/png;base64,{b64}"}

        # Brand foto: /api/brands/{slug}/foto/file — le do Mongo
        m = re.search(r"/brands/([^/]+)/foto/file", url)
        if m:
            slug = m.group(1)
            from services.brand_service import buscar_foto_brand
            result = buscar_foto_brand(slug)
            if result.get("foto"):
                return {"data_uri": result["foto"]}

        # Fallback: fetch via httpx (para outras URLs internas)
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            res.raise_for_status()
            mime = res.headers.get("content-type", "image/png")
            b64 = base64.b64encode(res.content).decode()
            return {"data_uri": f"data:{mime};base64,{b64}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
