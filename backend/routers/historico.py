from fastapi import APIRouter, HTTPException, Depends

from services.db_service import listar_historico as listar_historico_legado, deletar_historico as deletar_historico_legado

from config import settings
TENANT_ID = settings.TENANT_ID

router = APIRouter(tags=["Historico"])


def _get_service():
    """Tenta criar HistoricoService com SQL. Retorna None se SQL nao disponivel."""
    try:
        from data.connections.sql_connection import get_engine
        get_engine()  # levanta RuntimeError se MSSQL_URL nao configurado
    except Exception:
        return None
    return "sql_available"


@router.get("/historico")
async def listar_historico(
    texto: str | None = None,
    formato: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    filters = {}
    if texto:
        filters["texto"] = texto
    if formato:
        filters["formato"] = formato
    if status:
        filters["status"] = status

    # Tentar SQL primeiro
    if _get_service():
        try:
            from data.connections.database import get_sql_session_context
            from data.repositories.sql.historico_repository import HistoricoRepository
            from services.historico_service import HistoricoService
            async with get_sql_session_context() as session:
                repo = HistoricoRepository(session)
                service = HistoricoService(repo)
                return await service.listar(tenant_id=TENANT_ID, filters=filters)
        except Exception:
            pass

    # Fallback legado
    try:
        items = await listar_historico_legado(limit=limit)
        return {"items": items, "total": len(items)}
    except Exception:
        return {"items": [], "total": 0}


@router.get("/historico/{item_id}")
async def buscar_historico(item_id: str):
    if _get_service():
        try:
            from data.connections.database import get_sql_session_context
            from data.repositories.sql.historico_repository import HistoricoRepository
            from services.historico_service import HistoricoService
            async with get_sql_session_context() as session:
                repo = HistoricoRepository(session)
                service = HistoricoService(repo)
                result = await service.buscar(item_id, tenant_id=TENANT_ID)
                if not result:
                    raise HTTPException(status_code=404, detail="Item nao encontrado")
                return result
        except HTTPException:
            raise
        except Exception:
            pass
    raise HTTPException(status_code=404, detail="Item nao encontrado")


@router.delete("/historico/{item_id}")
async def deletar_historico(item_id: str):
    if _get_service():
        try:
            from data.connections.database import get_sql_session_context
            from data.repositories.sql.historico_repository import HistoricoRepository
            from services.historico_service import HistoricoService
            async with get_sql_session_context() as session:
                repo = HistoricoRepository(session)
                service = HistoricoService(repo)
                ok = await service.deletar(item_id, tenant_id=TENANT_ID)
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
