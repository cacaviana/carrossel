from sqlalchemy import select

from data.repositories.sql.base_sql_repository import BaseSQLRepository
from models.conteudo import ConteudoModel


class ConteudoRepository(BaseSQLRepository[ConteudoModel]):

    def __init__(self, session):
        super().__init__(session, ConteudoModel)

    async def buscar_por_pipeline(self, pipeline_id: str, tenant_id: str):
        result = await self._session.execute(
            select(ConteudoModel).where(
                ConteudoModel.pipeline_id == pipeline_id,
                ConteudoModel.tenant_id == tenant_id,
                ConteudoModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()
