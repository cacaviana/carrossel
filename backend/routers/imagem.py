import os

from fastapi import APIRouter, HTTPException, Request

from dtos.imagem.gerar_imagem.request import GerarImagemRequest, GerarImagemSlideRequest
from dtos.imagem.gerar_imagem.response import GerarImagemResponse, GerarImagemSlideResponse
from services.imagem_service import gerar_imagens, gerar_imagem_slide
from middleware.rate_limiter import limiter

router = APIRouter()


@router.post("/gerar-imagem", response_model=GerarImagemResponse)
@limiter.limit("5/minute")
async def api_gerar_imagem(request: Request, req: GerarImagemRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="GEMINI_API_KEY não configurada. Acesse /configuracoes.")
    try:
        slides_dicts = [s.model_dump() for s in req.slides]
        brand = req.brand_slug
        if not brand:
            from services.brand_prompt_builder import listar_brands
            brands = listar_brands()
            brand = brands[0]["slug"] if brands else ""
        from services.smart_image_service import gerar_imagens_smart
        images = await gerar_imagens_smart(slides=slides_dicts, gemini_api_key=api_key, brand_slug=brand, formato=req.formato)
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gerar-imagem-slide", response_model=GerarImagemSlideResponse)
@limiter.limit("5/minute")
async def api_gerar_imagem_slide(request: Request, req: GerarImagemSlideRequest):
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
        )
        return {"image": image}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
