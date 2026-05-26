from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from data.interfaces.base_repository import BaseRepository, T


class BaseSQLRepository(BaseRepository[T]):

    def __init__(self, session: AsyncSession, model_class: type):
        self._session = session
        self._model = model_class

    async def get_by_id(self, id: str, tenant_id: str):
        result = await self._session.execute(
            select(self._model).where(
                self._model.id == id,
                self._model.tenant_id == tenant_id,
                self._model.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(self, tenant_id: str, filters: dict = {}):
        stmt = select(self._model).where(
            self._model.tenant_id == tenant_id,
            self._model.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, id: str, entity: T, tenant_id: str) -> T:
        entity.updated_at = datetime.now(timezone.utc)
        await self._session.flush()
        return entity

    async def soft_delete(self, id: str, tenant_id: str) -> bool:
        obj = await self.get_by_id(id, tenant_id)
        if not obj:
            return False
        obj.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()
        return True
