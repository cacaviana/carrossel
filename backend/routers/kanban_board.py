from fastapi import APIRouter, HTTPException, Depends

from dtos.kanban_board.buscar_board.response import BoardResponse
from middleware.auth import get_current_user, CurrentUser
from services.kanban_board_service import KanbanBoardService

router = APIRouter(prefix="/kanban", tags=["Kanban Board"])


@router.get("/board", response_model=BoardResponse)
async def buscar_board_padrao(
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanBoardService.buscar_padrao(tenant_id=current_user.tenant_id)


@router.get("/boards/{board_id}", response_model=BoardResponse)
async def buscar_board(
    board_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    result = KanbanBoardService.buscar(board_id, tenant_id=current_user.tenant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Board nao encontrado")
    return result
