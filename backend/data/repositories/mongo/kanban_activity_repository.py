from data.connections.mongo_connection import get_mongo_db


class KanbanActivityRepository:

    @staticmethod
    def criar(doc: dict) -> dict:
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB nao configurado")
        result = db.kanban_activity_log.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def listar_por_card(card_id: str, tenant_id: str, limit: int = 50, skip: int = 0) -> list[dict]:
        db = get_mongo_db()
        if db is None:
            return []
        return list(
            db.kanban_activity_log.find({
                "card_id": card_id,
                "tenant_id": tenant_id,
            }).sort("created_at", -1).skip(skip).limit(limit)
        )
