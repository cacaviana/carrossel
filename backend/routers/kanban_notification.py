from fastapi import APIRouter, Depends, Query

from dtos.kanban_notification.listar_notificacoes.response import NotificacaoResponse
from dtos.kanban_notification.contar_nao_lidas.response import ContadorNaoLidasResponse
from dtos.kanban_activity.listar_atividades.response import AtividadeResponse
from middleware.auth import get_current_user, CurrentUser
from services.kanban_notification_service import KanbanNotificationService
from services.kanban_activity_service import KanbanActivityService

router = APIRouter(tags=["Kanban Notificacoes"])


@router.get("/kanban/notifications", response_model=list[NotificacaoResponse])
async def listar_notificacoes(
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanNotificationService.listar(
        user_id=current_user.user_id,
        tenant_id=current_user.tenant_id,
    )


@router.get("/kanban/notifications/count", response_model=ContadorNaoLidasResponse)
async def contar_nao_lidas(
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanNotificationService.contar_nao_lidas(
        user_id=current_user.user_id,
        tenant_id=current_user.tenant_id,
    )


@router.patch("/kanban/notifications/{notification_id}/read")
async def marcar_como_lida(
    notification_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanNotificationService.marcar_como_lida(
        notification_id, tenant_id=current_user.tenant_id
    )


@router.patch("/kanban/notifications/read-all")
async def marcar_todas_lidas(
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanNotificationService.marcar_todas_lidas(
        user_id=current_user.user_id,
        tenant_id=current_user.tenant_id,
    )


@router.get("/kanban/cards/{card_id}/activities", response_model=list[AtividadeResponse])
async def listar_atividades(
    card_id: str,
    limit: int = Query(50, le=200),
    skip: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanActivityService.listar(
        card_id, tenant_id=current_user.tenant_id, limit=limit, skip=skip
    )
