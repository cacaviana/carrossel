from sqlalchemy import select

from data.repositories.sql.base_sql_repository import BaseSQLRepository
from models.historico import HistoricoModel


class HistoricoRepository(BaseSQLRepository[HistoricoModel]):

    def __init__(self, session):
        super().__init__(session, HistoricoModel)

    async def list(self, tenant_id: str, filters: dict = {}):
        stmt = select(HistoricoModel).where(
            HistoricoModel.tenant_id == tenant_id,
            HistoricoModel.deleted_at.is_(None),
        ).order_by(HistoricoModel.created_at.desc())

        if "formato" in filters:
            stmt = stmt.where(HistoricoModel.formato == filters["formato"])
        if "status" in filters:
            stmt = stmt.where(HistoricoModel.status == filters["status"])
        if "texto" in filters:
            stmt = stmt.where(HistoricoModel.titulo.contains(filters["texto"]))

        result = await self._session.execute(stmt)
        return result.scalars().all()
