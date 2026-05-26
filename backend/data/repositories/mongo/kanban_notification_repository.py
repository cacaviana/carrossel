from bson import ObjectId
from data.connections.mongo_connection import get_mongo_db


class KanbanNotificationRepository:

    @staticmethod
    def criar(doc: dict) -> dict:
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB nao configurado")
        result = db.kanban_notifications.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def listar(user_id: str, tenant_id: str, limit: int = 20) -> list[dict]:
        db = get_mongo_db()
        if db is None:
            return []
        docs = list(db.kanban_notifications.find({
            "user_id": user_id,
            "tenant_id": tenant_id,
        }))
        docs.sort(key=lambda d: d.get("created_at", ""), reverse=True)
        return docs[:limit]

    @staticmethod
    def contar_nao_lidas(user_id: str, tenant_id: str) -> int:
        db = get_mongo_db()
        if db is None:
            return 0
        return db.kanban_notifications.count_documents({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "is_read": False,
        })

    @staticmethod
    def marcar_como_lida(notification_id: str, tenant_id: str) -> bool:
        db = get_mongo_db()
        if db is None:
            return False
        result = db.kanban_notifications.update_one(
            {"_id": ObjectId(notification_id), "tenant_id": tenant_id},
            {"$set": {"is_read": True}},
        )
        return result.modified_count > 0

    @staticmethod
    def marcar_todas_lidas(user_id: str, tenant_id: str) -> int:
        db = get_mongo_db()
        if db is None:
            return 0
        result = db.kanban_notifications.update_many(
            {"user_id": user_id, "tenant_id": tenant_id, "is_read": False},
            {"$set": {"is_read": True}},
        )
        return result.modified_count
