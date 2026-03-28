from fastapi import APIRouter, HTTPException

from dtos.publicacao.publicar.request import PublicarRequest
from dtos.publicacao.publicar.response import PublicarResponse
from services.publicacao_service import publicar_todas

router = APIRouter()


@router.post("/publicar", response_model=PublicarResponse)
async def api_publicar(req: PublicarRequest):
    try:
        resultados = await publicar_todas(
            images_base64=req.images_base64,
            legenda_instagram=req.legenda_instagram,
            texto_linkedin=req.texto_linkedin,
        )
        return {"resultados": resultados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
