"""Repository MongoDB para formatos de conteudo.

Collection: formatos (id como chave logica).
"""

from data.connections.mongo_connection import get_mongo_db


class FormatoRepository:
    """CRUD de formatos no MongoDB."""

    @staticmethod
    def listar() -> list[dict]:
        db = get_mongo_db()
        if db is None:
            return []
        return list(db.formatos.find({}, {"_id": 0}))

    @staticmethod
    def buscar(formato_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        return db.formatos.find_one({"id": formato_id}, {"_id": 0})

    @staticmethod
    def salvar(formato: dict) -> None:
        db = get_mongo_db()
        if db is None:
            return
        db.formatos.replace_one({"id": formato["id"]}, formato, upsert=True)
