import re
from bson import ObjectId
from datetime import datetime, timezone
from data.connections.mongo_connection import get_mongo_db


class KanbanCardRepository:

    @staticmethod
    def criar(doc: dict) -> dict:
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB nao configurado")
        result = db.kanban_cards.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def buscar_por_id(card_id: str, tenant_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        try:
            oid = ObjectId(card_id)
        except Exception:
            return None
        return db.kanban_cards.find_one({
            "_id": oid,
            "tenant_id": tenant_id,
            "archived_at": None,
        })

    @staticmethod
    def buscar_por_pipeline_id(pipeline_id: str, tenant_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        return db.kanban_cards.find_one({
            "pipeline_id": pipeline_id,
            "tenant_id": tenant_id,
            "archived_at": None,
        })

    @staticmethod
    def listar(tenant_id: str, filters: dict = {}) -> list[dict]:
        db = get_mongo_db()
        if db is None:
            return []
        query = {"tenant_id": tenant_id, "archived_at": None}
        if filters.get("board_id"):
            query["board_id"] = filters["board_id"]
        if filters.get("column_id"):
            query["column_id"] = filters["column_id"]
        if filters.get("priority"):
            query["priority"] = filters["priority"]
        if filters.get("assigned_user_id"):
            query["assigned_user_ids"] = filters["assigned_user_id"]
        if filters.get("search"):
            query["title"] = {"$regex": re.escape(filters["search"]), "$options": "i"}
        docs = list(db.kanban_cards.find(query))
        # Sort in-memory (CosmosDB requer index explicito pra sort)
        docs.sort(key=lambda d: d.get("created_at", ""), reverse=True)
        return docs

    @staticmethod
    def listar_com_deadline(tenant_id: str, inicio, fim) -> list[dict]:
        """Retorna cards com deadline dentro do intervalo [inicio, fim] (datetime aware).
        Usado pela view de calendario."""
        db = get_mongo_db()
        if db is None:
            return []
        query = {
            "tenant_id": tenant_id,
            "archived_at": None,
            "deadline": {"$gte": inicio, "$lte": fim},
        }
        docs = list(db.kanban_cards.find(query))
        docs.sort(key=lambda d: d.get("deadline") or d.get("created_at", ""))
        return docs

    @staticmethod
    def atualizar(card_id: str, tenant_id: str, fields: dict) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        try:
            oid = ObjectId(card_id)
        except Exception:
            return None
        db.kanban_cards.update_one(
            {"_id": oid, "tenant_id": tenant_id},
            {"$set": fields},
        )
        return db.kanban_cards.find_one({"_id": oid})

    @staticmethod
    def mover(card_id: str, tenant_id: str, column_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        try:
            oid = ObjectId(card_id)
        except Exception:
            return None
        db.kanban_cards.update_one(
            {"_id": oid, "tenant_id": tenant_id},
            {"$set": {
                "column_id": column_id,
                "updated_at": datetime.now(timezone.utc),
            }},
        )
        return db.kanban_cards.find_one({"_id": oid})

    @staticmethod
    def atribuir_responsaveis(card_id: str, tenant_id: str, user_ids: list[str]) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        try:
            oid = ObjectId(card_id)
        except Exception:
            return None
        db.kanban_cards.update_one(
            {"_id": oid, "tenant_id": tenant_id},
            {"$set": {
                "assigned_user_ids": user_ids,
                "updated_at": datetime.now(timezone.utc),
            }},
        )
        return db.kanban_cards.find_one({"_id": oid})
