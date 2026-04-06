from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):

    @abstractmethod
    async def get_by_id(self, id: str, tenant_id: str) -> Optional[T]:
        ...

    @abstractmethod
    async def list(self, tenant_id: str, filters: dict = {}) -> List[T]:
        ...

    @abstractmethod
    async def create(self, entity: T) -> T:
        ...

    @abstractmethod
    async def update(self, id: str, entity: T, tenant_id: str) -> T:
        ...

    @abstractmethod
    async def soft_delete(self, id: str, tenant_id: str) -> bool:
        ...
