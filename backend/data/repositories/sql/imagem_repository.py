from sqlalchemy import select

from data.repositories.sql.base_sql_repository import BaseSQLRepository
from models.imagem import ImagemModel


class ImagemRepository(BaseSQLRepository[ImagemModel]):

    def __init__(self, session):
        super().__init__(session, ImagemModel)

    async def listar_por_conteudo(self, conteudo_id: str, tenant_id: str):
        result = await self._session.execute(
            select(ImagemModel).where(
                ImagemModel.conteudo_id == conteudo_id,
                ImagemModel.tenant_id == tenant_id,
                ImagemModel.deleted_at.is_(None),
            ).order_by(ImagemModel.slide_index, ImagemModel.variacao)
        )
        return result.scalars().all()

    async def listar_selecionadas(self, conteudo_id: str, tenant_id: str):
        result = await self._session.execute(
            select(ImagemModel).where(
                ImagemModel.conteudo_id == conteudo_id,
                ImagemModel.tenant_id == tenant_id,
                ImagemModel.selecionada == True,
                ImagemModel.deleted_at.is_(None),
            ).order_by(ImagemModel.slide_index)
        )
        return result.scalars().all()
