from sqlalchemy import select
from sqlalchemy.orm import selectinload

from data.repositories.sql.base_sql_repository import BaseSQLRepository
from models.pipeline import PipelineModel, PipelineStepModel


class PipelineRepository(BaseSQLRepository[PipelineModel]):

    def __init__(self, session):
        super().__init__(session, PipelineModel)

    async def get_by_id(self, id: str, tenant_id: str):
        result = await self._session.execute(
            select(PipelineModel)
            .options(selectinload(PipelineModel.etapas))
            .where(
                PipelineModel.id == id,
                PipelineModel.tenant_id == tenant_id,
                PipelineModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(self, tenant_id: str, filters: dict = {}):
        stmt = select(PipelineModel).where(
            PipelineModel.tenant_id == tenant_id,
            PipelineModel.deleted_at.is_(None),
        ).order_by(PipelineModel.created_at.desc())

        if "formato" in filters:
            stmt = stmt.where(PipelineModel.formato == filters["formato"])
        if "status" in filters:
            stmt = stmt.where(PipelineModel.status == filters["status"])

        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def buscar_etapa(self, pipeline_id: str, agente: str, tenant_id: str):
        pipeline = await self.get_by_id(pipeline_id, tenant_id)
        if not pipeline:
            return None
        result = await self._session.execute(
            select(PipelineStepModel).where(
                PipelineStepModel.pipeline_id == pipeline_id,
                PipelineStepModel.agente == agente,
            )
        )
        return result.scalar_one_or_none()
