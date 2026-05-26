"""Router do dominio Anuncio (pos-pivot 2026-04-23).

Endpoints:
  POST   /api/anuncios                          criar + disparar pipeline
  GET    /api/anuncios                          listar com filtros
  GET    /api/anuncios/{id}                     detalhe hidratado
  PUT    /api/anuncios/{id}                     editar copy/metadados
  DELETE /api/anuncios/{id}                     soft delete
  POST   /api/anuncios/{id}/regenerar-imagem    regera imagem inteira (RN-018)
  POST   /api/anuncios/{id}/exportar            png (base64) ou drive

Compatibilidade com frontend atual:
  PUT    /api/anuncios/{id}/copy                alias de PUT /{id} (aceita CTA)
"""
from fastapi import APIRouter, Depends, HTTPException, Query

from middleware.auth import CurrentUser, get_current_user
from services.anuncio_service import AnuncioService

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


router = APIRouter(prefix="/anuncios", tags=["Anuncios"])


# -------------------- CREATE --------------------
@router.post("", response_model=CriarAnuncioResponse, status_code=201)
async def criar_anuncio(
    dto: CriarAnuncioRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: AnuncioService = Depends(),
):
    try:
        return await service.criar(dto, current_user.tenant_id, current_user.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------- LIST --------------------
@router.get("")
async def listar_anuncios(
    q: str | None = Query(default=None, description="Busca por titulo/headline"),
    status: str | None = Query(default=None),
    etapa_funil: str | None = Query(default=None),
    data_inicio: str | None = Query(default=None),
    data_fim: str | None = Query(default=None),
    incluir_excluidos: int | bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    service: AnuncioService = Depends(),
):
    incluir_b = bool(int(incluir_excluidos)) if isinstance(incluir_excluidos, str) else bool(incluir_excluidos)
    dto = ListarAnunciosRequest(
        busca=q,
        status=status,
        etapa_funil=etapa_funil,
        data_inicio=data_inicio,
        data_fim=data_fim,
        incluir_excluidos=incluir_b,
        page=page,
        page_size=page_size,
    )
    return await service.listar(dto, current_user.tenant_id)


# -------------------- GET BY ID --------------------
@router.get("/{anuncio_id}", response_model=ObterAnuncioResponse)
async def obter_anuncio(
    anuncio_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    service: AnuncioService = Depends(),
):
    return await service.obter(anuncio_id, current_user.tenant_id)


# -------------------- UPDATE (PUT) --------------------
@router.put("/{anuncio_id}", response_model=EditarAnuncioResponse)
async def editar_anuncio(
    anuncio_id: str,
    dto: EditarAnuncioRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: AnuncioService = Depends(),
):
    return await service.editar(anuncio_id, dto, current_user.tenant_id)


# Compat com frontend: PUT /anuncios/{id}/copy (aceita headline, descricao, cta)
@router.put("/{anuncio_id}/copy", response_model=EditarAnuncioResponse)
async def editar_copy(
    anuncio_id: str,
    dto: EditarAnuncioRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: AnuncioService = Depends(),
):
    return await service.editar(anuncio_id, dto, current_user.tenant_id)


# -------------------- DELETE (soft) --------------------
@router.delete("/{anuncio_id}", response_model=ExcluirAnuncioResponse)
async def excluir_anuncio(
    anuncio_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    service: AnuncioService = Depends(),
):
    return await service.excluir(anuncio_id, current_user.tenant_id)


# -------------------- REGENERAR IMAGEM (RN-018) --------------------
@router.post("/{anuncio_id}/regenerar-imagem", response_model=RegenerarImagemResponse)
async def regenerar_imagem(
    anuncio_id: str,
    dto: RegenerarImagemRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: AnuncioService = Depends(),
):
    return await service.regenerar_imagem(anuncio_id, dto, current_user.tenant_id)


# -------------------- EXPORTAR --------------------
@router.post("/{anuncio_id}/exportar", response_model=ExportarAnuncioResponse)
async def exportar_anuncio(
    anuncio_id: str,
    dto: ExportarAnuncioRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: AnuncioService = Depends(),
):
    return await service.exportar(anuncio_id, dto, current_user.tenant_id)
