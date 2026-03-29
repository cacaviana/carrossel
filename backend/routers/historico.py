from fastapi import APIRouter, HTTPException

from services.db_service import listar_historico, deletar_historico

router = APIRouter()


@router.get("/historico")
async def api_listar_historico():
    try:
        return await listar_historico(limit=50)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/historico/{item_id}")
async def api_deletar_historico(item_id: int):
    try:
        await deletar_historico(item_id)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
