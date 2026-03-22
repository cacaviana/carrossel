import os

from fastapi import APIRouter, HTTPException

from dtos.imagem.gerar_imagem.request import GerarImagemRequest, GerarImagemSlideRequest
from dtos.imagem.gerar_imagem.response import GerarImagemResponse, GerarImagemSlideResponse
from services.imagem_service import gerar_imagens, gerar_imagem_slide

router = APIRouter()


@router.post("/gerar-imagem", response_model=GerarImagemResponse)
async def api_gerar_imagem(req: GerarImagemRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="GEMINI_API_KEY não configurada. Acesse /configuracoes.")
    try:
        slides_dicts = [s.model_dump() for s in req.slides]
        images = await gerar_imagens(slides=slides_dicts, gemini_api_key=api_key, foto_criador=req.foto_criador)
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gerar-imagem-slide", response_model=GerarImagemSlideResponse)
async def api_gerar_imagem_slide(req: GerarImagemSlideRequest):
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
        )
        return {"image": image}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
