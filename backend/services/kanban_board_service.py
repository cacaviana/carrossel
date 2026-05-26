from mappers.kanban_board_mapper import KanbanBoardMapper
from data.repositories.mongo.kanban_board_repository import KanbanBoardRepository


class KanbanBoardService:

    @staticmethod
    def buscar_padrao(tenant_id: str):
        doc = KanbanBoardRepository.garantir_board_padrao(tenant_id)
        return KanbanBoardMapper.to_response(doc)

    @staticmethod
    def buscar(board_id: str, tenant_id: str):
        doc = KanbanBoardRepository.buscar_por_id(board_id, tenant_id)
        if not doc:
            return None
        return KanbanBoardMapper.to_response(doc)
