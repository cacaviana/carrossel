"""AnuncioService -- camada opaca do dominio Anuncio (pos-pivot 2026-04-23).

Nao conhece campos do DTO nem do Model. So orquestra:
    Factory (regras) + Repository (persistencia) + Mapper (conversao)
    + AnuncioPipelineService (pipeline externo)
    + AnuncioExportService (export)
"""
import os
from typing import Optional

from fastapi import Depends, HTTPException

from data.connections.database import get_sql_session
from data.repositories.sql.anuncio_repository import AnuncioRepository
from factories.anuncio_factory import AnuncioFactory
from mappers.anuncio_mapper import AnuncioMapper

from dtos.anuncio.criar_anuncio.request import CriarAnuncioRequest
from dtos.anuncio.criar_anuncio.response import CriarAnuncioResponse
from dtos.anuncio.listar_anuncios.request import ListarAnunciosRequest
from dtos.anuncio.obter_anuncio.response import ObterAnuncioResponse
from dtos.anuncio.editar_anuncio.request import EditarAnuncioRequest
from dtos.anuncio.editar_anuncio.response import EditarAnuncioResponse
from dtos.anuncio.excluir_anuncio.response import ExcluirAnuncioResponse
from dtos.anuncio.regenerar_imagem.request import RegenerarImagemRequest
from dtos.anuncio.regenerar_imagem.response import RegenerarImagemResponse
from dtos.anuncio.exportar_anuncio.request import ExportarAnuncioRequest
from dtos.anuncio.exportar_anuncio.response import ExportarAnuncioResponse

from services.anuncio_pipeline_service import AnuncioPipelineService
from services.anuncio_export_service import AnuncioExportService


class AnuncioService:
    """Camada opaca -- delega todo acesso a campos para Factory/Mapper/Repository."""

    def __init__(self, session=Depends(get_sql_session)):
        self.repo = AnuncioRepository(session)

    # ---------------- CRIAR ----------------
    async def criar(
        self, dto: CriarAnuncioRequest, tenant_id: str, criado_por: str,
    ) -> CriarAnuncioResponse:
        # 1. Buscar cta_anuncio default da marca (RN-024), se brand_slug informado
        cta_default = None
        if dto.brand_slug:
            try:
                from services.brand_service import buscar_brand
                brand = buscar_brand(dto.brand_slug)
                if brand:
                    cta_default = brand.get("cta_anuncio")
            except Exception:
                cta_default = None

        # 2. Iniciar pipeline formato=anuncio
        pipeline_id = await AnuncioPipelineService.iniciar_pipeline_anuncio(
            tema=dto.tema_ou_briefing or dto.titulo,
            modo_entrada=dto.modo_entrada,
            disciplina=dto.disciplina,
            tecnologia=dto.tecnologia,
            foto_criador_id=dto.foto_criador_id,
            etapa_funil=dto.etapa_funil,
            pipeline_funil_id=dto.pipeline_funil_id,
            tenant_id=tenant_id,
            brand_slug=dto.brand_slug,
        )

        # 3. Factory cria + valida
        try:
            anuncio = AnuncioFactory.criar(
                dto=dto,
                tenant_id=tenant_id,
                criado_por=criado_por,
                pipeline_id=pipeline_id,
                cta_default_marca=cta_default,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # 4. Persistir
        saved = await self.repo.create(anuncio)

        # 5. Mapper
        return AnuncioMapper.to_criar_response(saved)

    # ---------------- LISTAR ----------------
    async def listar(self, dto: ListarAnunciosRequest, tenant_id: str):
        items, _total = await self.repo.list_paginado(
            tenant_id=tenant_id,
            busca=dto.busca,
            status=dto.status,
            etapa_funil=dto.etapa_funil,
            data_inicio=dto.data_inicio,
            data_fim=dto.data_fim,
            incluir_excluidos=dto.incluir_excluidos,
            page=dto.page,
            page_size=dto.page_size,
        )
        return [AnuncioMapper.to_response(a) for a in items]

    # ---------------- OBTER ----------------
    async def obter(self, anuncio_id: str, tenant_id: str) -> ObterAnuncioResponse:
        anuncio = await self.repo.get_by_id(anuncio_id, tenant_id)
        if not anuncio:
            raise HTTPException(status_code=404, detail="Anuncio nao encontrado")
        return AnuncioMapper.to_obter_response(anuncio)

    # ---------------- EDITAR ----------------
    async def editar(
        self, anuncio_id: str, dto: EditarAnuncioRequest, tenant_id: str,
    ) -> EditarAnuncioResponse:
        anuncio = await self.repo.get_by_id(anuncio_id, tenant_id)
        if not anuncio:
            raise HTTPException(status_code=404, detail="Anuncio nao encontrado")
        try:
            AnuncioFactory.aplicar_edicao(anuncio, dto)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        await self.repo.update(anuncio)
        return AnuncioMapper.to_editar_response(anuncio)

    # ---------------- EXCLUIR (soft delete) ----------------
    async def excluir(self, anuncio_id: str, tenant_id: str) -> ExcluirAnuncioResponse:
        anuncio = await self.repo.get_by_id(anuncio_id, tenant_id)
        if not anuncio:
            raise HTTPException(status_code=404, detail="Anuncio nao encontrado")
        AnuncioFactory.preparar_soft_delete(anuncio)
        await self.repo.soft_delete_entity(anuncio)
        return AnuncioMapper.to_excluir_response(anuncio)

    # ---------------- REGENERAR IMAGEM (RN-018) ----------------
    async def regenerar_imagem(
        self, anuncio_id: str, dto: RegenerarImagemRequest, tenant_id: str,
    ) -> RegenerarImagemResponse:
        anuncio = await self.repo.get_by_id(anuncio_id, tenant_id)
        if not anuncio:
            raise HTTPException(status_code=404, detail="Anuncio nao encontrado")

        try:
            novo_pipeline_id = await AnuncioPipelineService.regenerar_imagem(
                anuncio=anuncio, tenant_id=tenant_id, feedback=dto.feedback,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Falha ao iniciar regeneracao: {e}")

        await self.repo.update(anuncio)

        return RegenerarImagemResponse(
            anuncio_id=str(anuncio.id),
            pipeline_id=novo_pipeline_id,
            status="em_andamento",
            message="Regeneracao da imagem iniciada",
        )

    # ---------------- EXPORTAR ----------------
    async def exportar(
        self, anuncio_id: str, dto: ExportarAnuncioRequest, tenant_id: str,
    ) -> ExportarAnuncioResponse:
        anuncio = await self.repo.get_by_id(anuncio_id, tenant_id)
        if not anuncio:
            raise HTTPException(status_code=404, detail="Anuncio nao encontrado")

        destino = (dto.destino or "png").lower()

        if destino == "png":
            image_b64, warning = await AnuncioExportService.build_png(anuncio)
            return ExportarAnuncioResponse(
                destino="png",
                image_base64=image_b64,
                arquivos_exportados=["anuncio.png"] if image_b64 else [],
                warning=warning,
            )

        if destino == "drive":
            credentials = os.getenv("GOOGLE_DRIVE_CREDENTIALS", "")
            parent = dto.drive_parent_folder_id or os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
            if not credentials:
                raise HTTPException(status_code=400, detail="GOOGLE_DRIVE_CREDENTIALS nao configurado")
            if not parent:
                raise HTTPException(
                    status_code=400,
                    detail="drive_parent_folder_id ou GOOGLE_DRIVE_FOLDER_ID obrigatorio",
                )

            folder_id, folder_link, arquivos, warning = await AnuncioExportService.salvar_drive(
                anuncio=anuncio,
                credentials_json=credentials,
                parent_folder_id=parent,
            )
            anuncio.drive_folder_id = folder_id
            anuncio.drive_folder_link = folder_link
            from datetime import datetime, timezone
            anuncio.last_exported_at = datetime.now(timezone.utc)
            await self.repo.update(anuncio)

            return ExportarAnuncioResponse(
                destino="drive",
                drive_folder_id=folder_id,
                drive_folder_link=folder_link,
                arquivos_exportados=arquivos,
                warning=warning,
            )

        raise HTTPException(status_code=400, detail=f"Destino invalido: {destino}")
