from fastapi import APIRouter, Depends

from dtos.kanban_comment.criar_comentario.request import CriarComentarioRequest
from dtos.kanban_comment.criar_comentario.response import ComentarioResponse
from dtos.kanban_comment.editar_comentario.request import EditarComentarioRequest
from middleware.auth import get_current_user, require_role, CurrentUser
from services.kanban_comment_service import KanbanCommentService

router = APIRouter(tags=["Kanban Comentarios"])


@router.post(
    "/kanban/cards/{card_id}/comments",
    response_model=ComentarioResponse,
    status_code=201,
)
async def criar_comentario(
    card_id: str,
    dto: CriarComentarioRequest,
    current_user: CurrentUser = Depends(
        require_role("admin", "copywriter", "designer", "reviewer")
    ),
):
    return KanbanCommentService.criar(
        card_id, dto,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        user_name=current_user.name,
    )


@router.get(
    "/kanban/cards/{card_id}/comments",
    response_model=list[ComentarioResponse],
)
async def listar_comentarios(
    card_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanCommentService.listar(card_id, tenant_id=current_user.tenant_id)


@router.patch("/kanban/comments/{comment_id}", response_model=ComentarioResponse)
async def editar_comentario(
    comment_id: str,
    dto: EditarComentarioRequest,
    current_user: CurrentUser = Depends(
        require_role("admin", "copywriter", "designer", "reviewer")
    ),
):
    return KanbanCommentService.editar(
        comment_id, dto,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        user_role=current_user.role,
    )


@router.delete("/kanban/comments/{comment_id}")
async def deletar_comentario(
    comment_id: str,
    current_user: CurrentUser = Depends(
        require_role("admin", "copywriter", "designer", "reviewer")
    ),
):
    return KanbanCommentService.deletar(
        comment_id,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        user_role=current_user.role,
    )
