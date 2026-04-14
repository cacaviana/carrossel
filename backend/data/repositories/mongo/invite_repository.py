"""Repository MongoDB para kanban_invite_tokens.

Collection: kanban_invite_tokens
TTL index em expires_at — MongoDB apaga automaticamente apos 48h.
NUNCA chama commit() — pymongo sincrono auto-commita.
"""

from datetime import datetime, timezone

from data.connections.mongo_connection import get_mongo_db


class InviteRepository:
    """CRUD de convites no MongoDB (kanban_invite_tokens)."""

    @staticmethod
    def insert_invite(doc: dict) -> dict:
        """Insere convite e retorna doc com _id preenchido."""
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB nao conectado")
        result = db.kanban_invite_tokens.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def find_by_token(token: str) -> dict | None:
        """Busca convite por token (nao filtra tenant — token e global unique)."""
        db = get_mongo_db()
        if db is None:
            return None
        return db.kanban_invite_tokens.find_one({"token": token})

    @staticmethod
    def mark_used(token: str) -> bool:
        """Marca convite como usado. Retorna True se encontrou e atualizou."""
        db = get_mongo_db()
        if db is None:
            return False
        result = db.kanban_invite_tokens.update_one(
            {"token": token},
            {"$set": {"used": True}},
        )
        return result.modified_count > 0

    @staticmethod
    def find_pending_by_email(tenant_id: str, email: str) -> dict | None:
        """Busca convite pendente (nao usado, nao expirado) por email+tenant."""
        db = get_mongo_db()
        if db is None:
            return None
        return db.kanban_invite_tokens.find_one({
            "tenant_id": tenant_id,
            "email": email.lower(),
            "used": False,
            "expires_at": {"$gt": datetime.now(timezone.utc)},
        })
