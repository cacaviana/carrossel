from sqlalchemy import select

from data.repositories.sql.base_sql_repository import BaseSQLRepository
from models.score import ScoreModel


class ScoreRepository(BaseSQLRepository[ScoreModel]):

    def __init__(self, session):
        super().__init__(session, ScoreModel)

    async def buscar_por_conteudo(self, conteudo_id: str, tenant_id: str):
        result = await self._session.execute(
            select(ScoreModel).where(
                ScoreModel.conteudo_id == conteudo_id,
                ScoreModel.tenant_id == tenant_id,
                ScoreModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()
