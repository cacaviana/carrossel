"""Conexao MongoDB (Cosmos DB com API Mongo).

Singleton — cria o client uma unica vez.
Retorna None se MONGO_URL nao estiver configurado (fallback seguro).
"""

import os

from pymongo import MongoClient

_client = None


def get_mongo_db():
    """Retorna database 'content_factory' ou None se sem conexao."""
    global _client
    if _client is None:
        mongo_url = os.getenv("MONGO_URL", "")
        if mongo_url is None or mongo_url == "":
            return None
        _client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    return _client["content_factory"]
