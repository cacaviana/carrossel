"""Seed do board padrao com 6 colunas fixas do MVP.

Colunas com IDs deterministicos (prefixo col-) para referencia em codigo.
Idempotente: so cria se nao existir board para o tenant.

Uso:
    cd backend
    python scripts/kanban_seed_board.py
"""

import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.connections.mongo_connection import get_mongo_db

# Tenant padrao para desenvolvimento local
DEFAULT_TENANT_ID = "itvalley-dev"

# Colunas fixas do MVP (RN-020)
# IDs deterministicos para referencia em codigo e testes
DEFAULT_COLUMNS = [
    {"id": "col-copy",       "name": "Copy",       "order": 0, "color": "#3B82F6", "auto_assign_user_ids": []},  # blue
    {"id": "col-design",     "name": "Design",     "order": 1, "color": "#8B5CF6", "auto_assign_user_ids": []},  # violet
    {"id": "col-revisao",    "name": "Revisao",    "order": 2, "color": "#F59E0B", "auto_assign_user_ids": []},  # amber
    {"id": "col-aprovado",   "name": "Aprovado",   "order": 3, "color": "#10B981", "auto_assign_user_ids": []},  # emerald
    {"id": "col-publicado",  "name": "Publicado",  "order": 4, "color": "#06B6D4", "auto_assign_user_ids": []},  # cyan
    {"id": "col-cancelado",  "name": "Cancelado",  "order": 5, "color": "#EF4444", "auto_assign_user_ids": []},  # red
]


def seed_board(tenant_id: str = DEFAULT_TENANT_ID):
    """Cria board padrao se nao existir para o tenant."""
    db = get_mongo_db()
    if db is None:
        print("ERRO: MONGO_URL nao configurado.")
        sys.exit(1)

    existing = db.kanban_boards.find_one({"tenant_id": tenant_id})
    if existing:
        print(f"  Board ja existe para tenant '{tenant_id}' (id={existing['_id']}). Nada a fazer.")
        return

    board = {
        "tenant_id": tenant_id,
        "name": "Pipeline de Carrosseis",
        "columns": DEFAULT_COLUMNS,
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
    }

    result = db.kanban_boards.insert_one(board)
    print(f"  Board criado: id={result.inserted_id}")
    print(f"  Tenant: {tenant_id}")
    print(f"  Colunas: {', '.join(c['name'] for c in DEFAULT_COLUMNS)}")


if __name__ == "__main__":
    print("=== Kanban: Seed Board Padrao ===\n")
    tenant = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TENANT_ID
    seed_board(tenant)
    print("\nDone.")
