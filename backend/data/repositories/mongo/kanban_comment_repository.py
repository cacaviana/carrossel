from bson import ObjectId
from datetime import datetime, timezone
from data.connections.mongo_connection import get_mongo_db


class KanbanCommentRepository:

    @staticmethod
    def criar(doc: dict) -> dict:
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB nao configurado")
        result = db.kanban_comments.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def listar_por_card(card_id: str, tenant_id: str) -> list[dict]:
        db = get_mongo_db()
        if db is None:
            return []
        docs = list(db.kanban_comments.find({
            "card_id": card_id,
            "tenant_id": tenant_id,
            "deleted_at": None,
        }))
        docs.sort(key=lambda d: d.get("created_at", ""))
        return docs

    @staticmethod
    def buscar_por_id(comment_id: str, tenant_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        return db.kanban_comments.find_one({
            "_id": ObjectId(comment_id),
            "tenant_id": tenant_id,
            "deleted_at": None,
        })

    @staticmethod
    def atualizar(comment_id: str, tenant_id: str, text: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        db.kanban_comments.update_one(
            {"_id": ObjectId(comment_id), "tenant_id": tenant_id},
            {"$set": {"text": text, "updated_at": datetime.now(timezone.utc)}},
        )
        return db.kanban_comments.find_one({"_id": ObjectId(comment_id)})

    @staticmethod
    def soft_delete(comment_id: str, tenant_id: str) -> bool:
        db = get_mongo_db()
        if db is None:
            return False
        result = db.kanban_comments.update_one(
            {"_id": ObjectId(comment_id), "tenant_id": tenant_id},
            {"$set": {"deleted_at": datetime.now(timezone.utc)}},
        )
        return result.modified_count > 0

    @staticmethod
    def contar_por_card(card_id: str, tenant_id: str) -> int:
        db = get_mongo_db()
        if db is None:
            return 0
        return db.kanban_comments.count_documents({
            "card_id": card_id,
            "tenant_id": tenant_id,
            "deleted_at": None,
        })
