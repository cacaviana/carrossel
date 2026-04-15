"""Cria indices otimizados para as collections do Kanban.

Indices baseados nos padroes de acesso do PRD (secao 6 e 10).
Todo indice inclui tenant_id como primeiro campo (isolamento multitenante).
Idempotente: pymongo ignora create_index se indice ja existe.

Uso:
    cd backend
    python scripts/kanban_setup_indexes.py
"""

import os
import sys

import pymongo

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.connections.mongo_connection import get_mongo_db


def _safe_index(coll, keys, **kwargs):
    """Cria indice ignorando erros de compatibilidade (CosmosDB)."""
    name = kwargs.get("name", str(keys))
    try:
        coll.create_index(keys, **kwargs)
        return True
    except Exception as e:
        # CosmosDB nao suporta unique em compound, TTL, sparse etc
        # Tenta sem opcoes especiais
        try:
            simple_kwargs = {"name": name}
            coll.create_index(keys, **simple_kwargs)
            return True
        except Exception:
            print(f"    WARN: indice '{name}' nao criado ({e})")
            return False


def setup_indexes():
    db = get_mongo_db()
    if db is None:
        print("ERRO: MONGO_URL nao configurado.")
        sys.exit(1)

    created = 0

    # ----- kanban_users -----
    coll = db.kanban_users
    created += _safe_index(coll, [("tenant_id", 1), ("email", 1)],
                           unique=True, name="idx_users_tenant_email_unique")
    created += _safe_index(coll, [("tenant_id", 1), ("deleted_at", 1)],
                           name="idx_users_tenant_active")
    print("  kanban_users: indices processados")

    # ----- kanban_boards -----
    coll = db.kanban_boards
    created += _safe_index(coll, [("tenant_id", 1)], name="idx_boards_tenant")
    print("  kanban_boards: indices processados")

    # ----- kanban_cards -----
    coll = db.kanban_cards
    created += _safe_index(coll, [("tenant_id", 1), ("board_id", 1), ("column_id", 1)],
                           name="idx_cards_tenant_board_column")
    created += _safe_index(coll, [("tenant_id", 1), ("assigned_user_ids", 1)],
                           name="idx_cards_tenant_assigned")
    created += _safe_index(coll, [("tenant_id", 1), ("board_id", 1), ("priority", 1)],
                           name="idx_cards_tenant_board_priority")
    created += _safe_index(coll, [("tenant_id", 1), ("pipeline_id", 1)],
                           name="idx_cards_tenant_pipeline", sparse=True)
    created += _safe_index(coll, [("tenant_id", 1), ("board_id", 1), ("archived_at", 1)],
                           name="idx_cards_tenant_board_archived")
    print("  kanban_cards: indices processados")

    # ----- kanban_comments -----
    coll = db.kanban_comments
    created += _safe_index(coll, [("tenant_id", 1), ("card_id", 1), ("created_at", 1)],
                           name="idx_comments_tenant_card_date")
    print("  kanban_comments: indices processados")

    # ----- kanban_activity_log -----
    coll = db.kanban_activity_log
    created += _safe_index(coll, [("tenant_id", 1), ("card_id", 1), ("created_at", -1)],
                           name="idx_activity_tenant_card_date")
    print("  kanban_activity_log: indices processados")

    # ----- kanban_notifications -----
    coll = db.kanban_notifications
    created += _safe_index(coll, [("tenant_id", 1), ("user_id", 1), ("is_read", 1)],
                           name="idx_notifications_tenant_user_read")
    created += _safe_index(coll, [("tenant_id", 1), ("user_id", 1), ("is_read", 1), ("created_at", -1)],
                           name="idx_notifications_tenant_user_read_date")
    print("  kanban_notifications: indices processados")

    # ----- kanban_invite_tokens -----
    coll = db.kanban_invite_tokens
    created += _safe_index(coll, [("token", 1)], unique=True,
                           name="idx_invite_token_unique")
    created += _safe_index(coll, [("expires_at", 1)], expireAfterSeconds=0,
                           name="idx_invite_ttl")
    created += _safe_index(coll, [("tenant_id", 1), ("email", 1)],
                           name="idx_invite_tenant_email")
    print("  kanban_invite_tokens: indices processados")

    print(f"\nTotal: {created}/15 indices criados/verificados.")


if __name__ == "__main__":
    print("=== Kanban: Setup Indexes ===\n")
    setup_indexes()
    print("\nDone.")
