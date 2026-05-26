"""Endpoint para sobrepor foto real do criador nos slides na hora do export."""
from fastapi import APIRouter, Depends, HTTPException

from dtos.foto_overlay.aplicar_foto.request import AplicarFotoRequest
from dtos.foto_overlay.aplicar_foto.response import AplicarFotoResponse
from dtos.foto_overlay.aplicar_foto_batch.request import AplicarFotoBatchRequest
from dtos.foto_overlay.aplicar_foto_batch.response import AplicarFotoBatchResponse
from middleware.auth import CurrentUser, get_current_user
from services.foto_overlay import overlay_foto

router = APIRouter(tags=["Foto Overlay"])


@router.post("/aplicar-foto", response_model=AplicarFotoResponse)
async def api_aplicar_foto(
    req: AplicarFotoRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    try:
        result = overlay_foto(req.slide_image, req.foto_criador, is_cta=req.is_cta)
        return {"image": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/aplicar-foto-batch", response_model=AplicarFotoBatchResponse)
async def api_aplicar_foto_batch(
    req: AplicarFotoBatchRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Aplica foto em todos os slides de uma vez. Ultimo slide = CTA (foto grande)."""
    try:
        results = []
        total = len(req.slides)
        for i, slide in enumerate(req.slides):
            is_cta = (i == total - 1)
            result = overlay_foto(slide, req.foto_criador, is_cta=is_cta)
            results.append(result)
        return {"images": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
