"""Repository MongoDB para kanban_users.

Collection: kanban_users
Todas as queries filtram por tenant_id (multitenante).
NUNCA chama commit() — pymongo sincrono auto-commita.
"""

from datetime import datetime, timezone

from bson import ObjectId

from data.connections.mongo_connection import get_mongo_db


class AuthRepository:
    """CRUD de usuarios no MongoDB (kanban_users)."""

    @staticmethod
    def find_by_email(tenant_id: str, email: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        return db.kanban_users.find_one({
            "tenant_id": tenant_id,
            "email": email.lower(),
        })

    @staticmethod
    def find_by_id(tenant_id: str, user_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        return db.kanban_users.find_one({
            "_id": oid,
            "tenant_id": tenant_id,
        })

    @staticmethod
    def find_all_by_tenant(tenant_id: str) -> list[dict]:
        """Lista usuarios do tenant, excluindo soft-deleted."""
        db = get_mongo_db()
        if db is None:
            return []
        return list(db.kanban_users.find({
            "tenant_id": tenant_id,
            "deleted_at": None,
        }).sort("created_at", 1))

    @staticmethod
    def insert_user(doc: dict) -> dict:
        """Insere usuario e retorna doc com _id preenchido."""
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB nao conectado")
        result = db.kanban_users.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def email_exists(tenant_id: str, email: str) -> bool:
        db = get_mongo_db()
        if db is None:
            return False
        return db.kanban_users.find_one({
            "tenant_id": tenant_id,
            "email": email.lower(),
        }) is not None

    @staticmethod
    def update_user(tenant_id: str, user_id: str, updates: dict) -> dict | None:
        """Atualiza campos do usuario. Retorna doc atualizado ou None."""
        db = get_mongo_db()
        if db is None:
            return None
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        result = db.kanban_users.find_one_and_update(
            {"_id": oid, "tenant_id": tenant_id},
            {"$set": updates},
            return_document=True,
        )
        return result

    @staticmethod
    def soft_delete(tenant_id: str, user_id: str) -> dict | None:
        """Soft delete: seta deleted_at. Retorna doc atualizado."""
        return AuthRepository.update_user(tenant_id, user_id, {
            "deleted_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        })

    @staticmethod
    def reactivate(tenant_id: str, user_id: str) -> dict | None:
        """Reativa usuario: limpa deleted_at. Retorna doc atualizado."""
        return AuthRepository.update_user(tenant_id, user_id, {
            "deleted_at": None,
            "updated_at": datetime.now(timezone.utc),
        })
