from dtos.kanban_board.buscar_board.response import BoardResponse
from dtos.kanban_board.base import ColunaBase


class KanbanBoardMapper:

    @staticmethod
    def to_response(doc: dict) -> BoardResponse:
        return BoardResponse(
            id=str(doc["_id"]),
            tenant_id=doc["tenant_id"],
            name=doc["name"],
            columns=[
                ColunaBase(
                    id=col["id"],
                    name=col["name"],
                    order=col["order"],
                    color=col.get("color"),
                )
                for col in doc.get("columns", [])
            ],
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at"),
        )
