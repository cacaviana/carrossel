"""Repository MongoDB para brands (design systems por marca).

Collection: brands (slug como chave logica).
"""

from data.connections.mongo_connection import get_mongo_db


class BrandRepository:
    """CRUD de brands no MongoDB."""

    @staticmethod
    def listar() -> list[dict]:
        db = get_mongo_db()
        if db is None:
            return []
        return list(db.brands.find({}, {"_id": 0}))

    @staticmethod
    def buscar(slug: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        return db.brands.find_one({"slug": slug}, {"_id": 0})

    @staticmethod
    def salvar(brand: dict) -> None:
        db = get_mongo_db()
        if db is None:
            return
        db.brands.replace_one({"slug": brand["slug"]}, brand, upsert=True)

    @staticmethod
    def deletar(slug: str) -> bool:
        db = get_mongo_db()
        if db is None:
            return False
        result = db.brands.delete_one({"slug": slug})
        return result.deleted_count > 0
