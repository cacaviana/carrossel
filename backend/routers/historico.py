from fastapi import APIRouter, Depends, HTTPException

from middleware.auth import CurrentUser, get_current_user
from services.db_service import listar_historico as listar_historico_legado, deletar_historico as deletar_historico_legado

from config import settings

router = APIRouter(tags=["Historico"])


def _sql_available():
    """Checa se MSSQL_URL esta configurado (nao testa conexao)."""
    try:
        if not settings.MSSQL_URL:
            return False
        return True
    except Exception:
        return False


@router.get("/historico")
async def listar_historico(
    texto: str | None = None,
    formato: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    current_user: CurrentUser = Depends(get_current_user),
):
    tenant_id = current_user.tenant_id
    filters = {}
    if texto:
        filters["texto"] = texto
    if formato:
        filters["formato"] = formato
    if status:
        filters["status"] = status

    # Tentar SQL primeiro
    if _sql_available():
        try:
            from data.connections.database import get_sql_session_context
            from data.repositories.sql.historico_repository import HistoricoRepository
            from services.historico_service import HistoricoService
            async with get_sql_session_context() as session:
                repo = HistoricoRepository(session)
                service = HistoricoService(repo)
                return await service.listar(tenant_id=tenant_id, filters=filters)
        except Exception:
            pass

    # Fallback legado
    try:
        items = await listar_historico_legado(limit=limit)
        return {"items": items, "total": len(items)}
    except Exception:
        return {"items": [], "total": 0}


@router.get("/historico/{item_id}")
async def buscar_historico(
    item_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    tenant_id = current_user.tenant_id
    if _sql_available():
        try:
            from data.connections.database import get_sql_session_context
            from data.repositories.sql.historico_repository import HistoricoRepository
            from services.historico_service import HistoricoService
            async with get_sql_session_context() as session:
                repo = HistoricoRepository(session)
                service = HistoricoService(repo)
                result = await service.buscar(item_id, tenant_id=tenant_id)
                if not result:
                    raise HTTPException(status_code=404, detail="Item nao encontrado")
                return result
        except HTTPException:
            raise
        except Exception:
            pass
    raise HTTPException(status_code=404, detail="Item nao encontrado")


@router.delete("/historico/{item_id}")
async def deletar_historico(
    item_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    tenant_id = current_user.tenant_id
    if _sql_available():
        try:
            from data.connections.database import get_sql_session_context
            from data.repositories.sql.historico_repository import HistoricoRepository
            from services.historico_service import HistoricoService
            async with get_sql_session_context() as session:
                repo = HistoricoRepository(session)
                service = HistoricoService(repo)
                ok = await service.deletar(item_id, tenant_id=tenant_id)
                if ok:
                    return {"ok": True}
        except Exception:
            pass

    # Fallback legado
    try:
        await deletar_historico_legado(int(item_id))
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
