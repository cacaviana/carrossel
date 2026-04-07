from fastapi import APIRouter, HTTPException, Depends

from dtos.historico.listar_historico.response import ListarHistoricoResponse
from dtos.historico.buscar_historico.response import BuscarHistoricoResponse
from services.historico_service import HistoricoService
from services.db_service import listar_historico as listar_historico_legado, deletar_historico as deletar_historico_legado
from data.connections.database import get_sql_session
from data.repositories.sql.historico_repository import HistoricoRepository

from config import settings
TENANT_ID = settings.TENANT_ID

router = APIRouter(tags=["Historico"])


def _get_service(session=Depends(get_sql_session)):
    repo = HistoricoRepository(session)
    return HistoricoService(repo)


@router.get("/historico", response_model=ListarHistoricoResponse)
async def listar_historico(
    texto: str | None = None,
    formato: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    service: HistoricoService = Depends(_get_service),
):
    filters = {}
    if texto:
        filters["texto"] = texto
    if formato:
        filters["formato"] = formato
    if status:
        filters["status"] = status
    try:
        return await service.listar(tenant_id=TENANT_ID, filters=filters)
    except Exception:
        # Fallback para legado se SQLAlchemy nao estiver configurado
        try:
            items = await listar_historico_legado(limit=limit)
            return {"items": items, "total": len(items)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/historico/{item_id}", response_model=BuscarHistoricoResponse)
async def buscar_historico(
    item_id: str,
    service: HistoricoService = Depends(_get_service),
):
    result = await service.buscar(item_id, tenant_id=TENANT_ID)
    if not result:
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    return result


@router.delete("/historico/{item_id}")
async def deletar_historico(
    item_id: str,
    service: HistoricoService = Depends(_get_service),
):
    try:
        ok = await service.deletar(item_id, tenant_id=TENANT_ID)
        if not ok:
            raise HTTPException(status_code=404, detail="Item nao encontrado")
        return {"ok": True}
    except Exception:
        # Fallback para legado
        try:
            await deletar_historico_legado(int(item_id))
            return {"ok": True}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
