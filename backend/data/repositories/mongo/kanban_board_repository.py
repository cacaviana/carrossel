from bson import ObjectId
from data.connections.mongo_connection import get_mongo_db


class KanbanBoardRepository:

    @staticmethod
    def buscar_padrao(tenant_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        return db.kanban_boards.find_one({"tenant_id": tenant_id})

    @staticmethod
    def buscar_por_id(board_id: str, tenant_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        return db.kanban_boards.find_one({
            "_id": ObjectId(board_id),
            "tenant_id": tenant_id,
        })

    @staticmethod
    def criar(doc: dict) -> dict:
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB nao configurado")
        result = db.kanban_boards.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def garantir_board_padrao(tenant_id: str) -> dict:
        from factories.kanban_board_factory import KanbanBoardFactory
        board = KanbanBoardRepository.buscar_padrao(tenant_id)
        if board:
            return board
        doc = KanbanBoardFactory.criar_board_padrao(tenant_id)
        return KanbanBoardRepository.criar(doc)
