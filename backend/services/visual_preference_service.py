from factories.visual_preference_factory import VisualPreferenceFactory
from mappers.visual_preference_mapper import VisualPreferenceMapper
from data.interfaces.base_repository import BaseRepository


class VisualPreferenceService:

    def __init__(self, repo: BaseRepository):
        self._repo = repo

    async def salvar(self, dto, tenant_id: str):
        model = VisualPreferenceFactory.to_model(dto, tenant_id)
        saved = await self._repo.create(model)
        return VisualPreferenceMapper.to_salvar_response(saved)

    async def listar(self, tenant_id: str):
        models = await self._repo.list(tenant_id)
        items = VisualPreferenceMapper.to_list(models)
        return {"items": items}
