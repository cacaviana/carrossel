"""Repository MongoDB para tenants.

Collection: tenants
Queries nao filtram por tenant_id (tenants sao o registro raiz).
Acesso so eh liberado pelo role super_admin (controle no router).
"""

from datetime import datetime, timezone

from data.connections.mongo_connection import get_mongo_db


class TenantRepository:

    @staticmethod
    def criar(doc: dict) -> dict:
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB nao configurado")
        result = db.tenants.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def find_by_tenant_id(tenant_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        return db.tenants.find_one({"tenant_id": tenant_id})

    @staticmethod
    def exists(tenant_id: str) -> bool:
        return TenantRepository.find_by_tenant_id(tenant_id) is not None

    @staticmethod
    def listar(limit: int, offset: int, status: str | None = None) -> tuple[list[dict], int]:
        """Retorna (items_paginados, total)."""
        db = get_mongo_db()
        if db is None:
            return [], 0
        query: dict = {}
        if status:
            query["status"] = status
        total = db.tenants.count_documents(query)
        cursor = db.tenants.find(query).skip(offset).limit(limit)
        docs = list(cursor)
        docs.sort(key=lambda d: d.get("created_at") or datetime.min, reverse=True)
        return docs, total

    @staticmethod
    def atualizar(tenant_id: str, fields: dict, audit_entry: dict | None = None) -> dict | None:
        """Atualiza campos + opcionalmente empurra entrada de auditoria no array."""
        db = get_mongo_db()
        if db is None:
            return None
        update: dict = {"$set": fields}
        if audit_entry:
            update["$push"] = {"audit_log": audit_entry}
        return db.tenants.find_one_and_update(
            {"tenant_id": tenant_id},
            update,
            return_document=True,
        )

    @staticmethod
    def atrelar_admin(tenant_id: str, admin_user_id: str) -> None:
        """Grava admin_user_id no doc do tenant apos criar o user admin."""
        db = get_mongo_db()
        if db is None:
            return
        db.tenants.update_one(
            {"tenant_id": tenant_id},
            {"$set": {"admin_user_id": admin_user_id, "updated_at": datetime.now(timezone.utc)}},
        )
