"""Repository do dominio Anuncio (pos-pivot 2026-04-23).
Estende BaseSQLRepository. Nao faz commit -- get_sql_session cuida disso.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func, or_

from data.repositories.sql.base_sql_repository import BaseSQLRepository
from models.anuncio import AnuncioModel


class AnuncioRepository(BaseSQLRepository[AnuncioModel]):

    def __init__(self, session):
        super().__init__(session, AnuncioModel)

    # ---------- GET ----------
    async def get_by_id(self, id: str, tenant_id: str) -> Optional[AnuncioModel]:
        result = await self._session.execute(
            select(AnuncioModel).where(
                AnuncioModel.id == id,
                AnuncioModel.tenant_id == tenant_id,
                AnuncioModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_incluindo_excluidos(self, id: str, tenant_id: str) -> Optional[AnuncioModel]:
        result = await self._session.execute(
            select(AnuncioModel).where(
                AnuncioModel.id == id,
                AnuncioModel.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_pipeline_id(self, pipeline_id: str, tenant_id: str) -> Optional[AnuncioModel]:
        result = await self._session.execute(
            select(AnuncioModel).where(
                AnuncioModel.pipeline_id == pipeline_id,
                AnuncioModel.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    # ---------- LIST ----------
    async def list_paginado(
        self,
        tenant_id: str,
        busca: Optional[str] = None,
        status: Optional[str] = None,
        etapa_funil: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        incluir_excluidos: bool = False,
        page: int = 1,
        page_size: int = 100,
    ) -> tuple[list[AnuncioModel], int]:
        stmt = select(AnuncioModel).where(AnuncioModel.tenant_id == tenant_id)

        if not incluir_excluidos:
            stmt = stmt.where(AnuncioModel.deleted_at.is_(None))
        if busca:
            stmt = stmt.where(
                or_(
                    AnuncioModel.titulo.like(f"%{busca}%"),
                    AnuncioModel.headline.like(f"%{busca}%"),
                )
            )
        # Traducao do status do frontend pro banco
        from mappers.anuncio_mapper import _STATUS_DB_TO_FRONT
        inv = {v: k for k, v in _STATUS_DB_TO_FRONT.items()}
        if status and status != "todos":
            status_db = inv.get(status, status)
            stmt = stmt.where(AnuncioModel.status == status_db)
        if etapa_funil and etapa_funil != "todas":
            stmt = stmt.where(AnuncioModel.etapa_funil == etapa_funil)
        if data_inicio:
            stmt = stmt.where(AnuncioModel.created_at >= data_inicio)
        if data_fim:
            stmt = stmt.where(AnuncioModel.created_at <= f"{data_fim}T23:59:59")

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self._session.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(AnuncioModel.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self._session.execute(stmt)
        items = result.scalars().all()
        return list(items), int(total)

    # ---------- CREATE / UPDATE ----------
    async def create(self, anuncio: AnuncioModel) -> AnuncioModel:
        self._session.add(anuncio)
        await self._session.flush()
        return anuncio

    async def update(self, anuncio: AnuncioModel) -> AnuncioModel:
        anuncio.updated_at = datetime.now(timezone.utc)
        await self._session.flush()
        return anuncio

    # ---------- DELETE ----------
    async def soft_delete_entity(self, anuncio: AnuncioModel) -> AnuncioModel:
        """Soft delete: deleted_at preenchido pelo Factory antes desta chamada."""
        await self._session.flush()
        return anuncio
