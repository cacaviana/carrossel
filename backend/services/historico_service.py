from factories.historico_factory import HistoricoFactory
from mappers.historico_mapper import HistoricoMapper
from data.interfaces.base_repository import BaseRepository


class HistoricoService:

    def __init__(self, repo: BaseRepository):
        self._repo = repo

    async def listar(self, tenant_id: str, filters: dict = {}):
        models = await self._repo.list(tenant_id, filters)
        items = HistoricoMapper.to_list(models)
        total = len(items)
        return {"items": items, "total": total}

    async def buscar(self, item_id: str, tenant_id: str):
        model = await self._repo.get_by_id(item_id, tenant_id)
        if not model:
            return None
        return HistoricoMapper.to_buscar_response(model)

    async def deletar(self, item_id: str, tenant_id: str):
        return await self._repo.soft_delete(item_id, tenant_id)
