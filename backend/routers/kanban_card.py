from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from dtos.kanban_card.criar_card.request import CriarCardRequest
from dtos.kanban_card.criar_card.response import CardResponse
from dtos.kanban_card.atualizar_card.request import AtualizarCardRequest
from dtos.kanban_card.mover_card.request import MoverCardRequest
from dtos.kanban_card.atribuir_responsaveis.request import AtribuirResponsaveisRequest
from dtos.kanban_card.vincular_artefato.request import VincularArtefatoRequest
from dtos.kanban_card.listar_calendario.response import ListarCalendarioResponse
from middleware.auth import get_current_user, require_role, CurrentUser
from services.kanban_card_service import KanbanCardService

router = APIRouter(prefix="/kanban/cards", tags=["Kanban Cards"])


@router.post("", response_model=CardResponse, status_code=201)
async def criar_card(
    dto: CriarCardRequest,
    current_user: CurrentUser = Depends(require_role("admin", "copywriter")),
):
    return KanbanCardService.criar(
        dto,
        tenant_id=current_user.tenant_id,
        created_by=current_user.user_id,
    )


@router.get("/calendario", response_model=ListarCalendarioResponse)
async def listar_calendario(
    mes: str = Query(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="YYYY-MM"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Lista cards com deadline dentro do mes. View de calendario para Historico."""
    return KanbanCardService.listar_calendario(
        tenant_id=current_user.tenant_id,
        mes=mes,
    )


@router.get("", response_model=list[CardResponse])
async def listar_cards(
    board_id: Optional[str] = Query(None),
    column_id: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_user_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
):
    filtros = {
        k: v for k, v in {
            "board_id": board_id,
            "column_id": column_id,
            "priority": priority,
            "assigned_user_id": assigned_user_id,
            "search": search,
        }.items() if v is not None
    }
    return KanbanCardService.listar(
        tenant_id=current_user.tenant_id,
        filtros=filtros,
    )


@router.get("/{card_id}", response_model=CardResponse)
async def buscar_card(
    card_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanCardService.buscar(card_id, tenant_id=current_user.tenant_id)


@router.patch("/{card_id}", response_model=CardResponse)
async def atualizar_card(
    card_id: str,
    dto: AtualizarCardRequest,
    current_user: CurrentUser = Depends(
        require_role("admin", "copywriter", "designer", "reviewer")
    ),
):
    return KanbanCardService.atualizar(
        card_id, dto,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
    )


@router.patch("/{card_id}/move", response_model=CardResponse)
async def mover_card(
    card_id: str,
    dto: MoverCardRequest,
    current_user: CurrentUser = Depends(
        require_role("admin", "copywriter", "designer", "reviewer")
    ),
):
    return KanbanCardService.mover_manual(
        card_id, dto,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
    )


@router.patch("/{card_id}/responsaveis", response_model=CardResponse)
async def atribuir_responsaveis(
    card_id: str,
    dto: AtribuirResponsaveisRequest,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    return KanbanCardService.atribuir_responsaveis(
        card_id, dto,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
    )


@router.patch("/{card_id}/artefatos", response_model=CardResponse)
async def vincular_artefato(
    card_id: str,
    dto: VincularArtefatoRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanCardService.vincular_artefato(
        card_id, dto,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
    )
