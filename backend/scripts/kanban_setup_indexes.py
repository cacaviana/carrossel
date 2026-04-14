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


def setup_indexes():
    db = get_mongo_db()
    if db is None:
        print("ERRO: MONGO_URL nao configurado.")
        sys.exit(1)

    # ----- kanban_users -----
    coll = db.kanban_users
    # Unique por tenant+email (login, busca de usuario)
    coll.create_index(
        [("tenant_id", 1), ("email", 1)],
        unique=True,
        name="idx_users_tenant_email_unique",
    )
    # Busca por tenant (listar usuarios)
    coll.create_index(
        [("tenant_id", 1), ("deleted_at", 1)],
        name="idx_users_tenant_active",
    )
    print("  kanban_users: 2 indices")

    # ----- kanban_boards -----
    coll = db.kanban_boards
    # Busca board por tenant (listar/buscar board padrao)
    coll.create_index(
        [("tenant_id", 1)],
        name="idx_boards_tenant",
    )
    print("  kanban_boards: 1 indice")

    # ----- kanban_cards -----
    coll = db.kanban_cards
    # Query principal do board: listar cards por board + coluna
    coll.create_index(
        [("tenant_id", 1), ("board_id", 1), ("column_id", 1)],
        name="idx_cards_tenant_board_column",
    )
    # Filtro por responsavel
    coll.create_index(
        [("tenant_id", 1), ("assigned_user_ids", 1)],
        name="idx_cards_tenant_assigned",
    )
    # Filtro por prioridade
    coll.create_index(
        [("tenant_id", 1), ("board_id", 1), ("priority", 1)],
        name="idx_cards_tenant_board_priority",
    )
    # Busca por pipeline_id (integracao com pipeline existente)
    coll.create_index(
        [("tenant_id", 1), ("pipeline_id", 1)],
        name="idx_cards_tenant_pipeline",
        sparse=True,
    )
    # Soft delete filter
    coll.create_index(
        [("tenant_id", 1), ("board_id", 1), ("archived_at", 1)],
        name="idx_cards_tenant_board_archived",
    )
    print("  kanban_cards: 5 indices")

    # ----- kanban_comments -----
    coll = db.kanban_comments
    # Listar comentarios de um card (cronologico)
    coll.create_index(
        [("tenant_id", 1), ("card_id", 1), ("created_at", 1)],
        name="idx_comments_tenant_card_date",
    )
    print("  kanban_comments: 1 indice")

    # ----- kanban_activity_log -----
    coll = db.kanban_activity_log
    # Timeline de atividade de um card (mais recente primeiro)
    coll.create_index(
        [("tenant_id", 1), ("card_id", 1), ("created_at", -1)],
        name="idx_activity_tenant_card_date",
    )
    print("  kanban_activity_log: 1 indice")

    # ----- kanban_notifications -----
    coll = db.kanban_notifications
    # Listar notificacoes do usuario (nao-lidas primeiro)
    coll.create_index(
        [("tenant_id", 1), ("user_id", 1), ("is_read", 1)],
        name="idx_notifications_tenant_user_read",
    )
    # Contador rapido de nao-lidas
    coll.create_index(
        [("tenant_id", 1), ("user_id", 1), ("is_read", 1), ("created_at", -1)],
        name="idx_notifications_tenant_user_read_date",
    )
    print("  kanban_notifications: 2 indices")

    # ----- kanban_invite_tokens -----
    coll = db.kanban_invite_tokens
    # Busca por token (aceitar convite)
    coll.create_index(
        [("token", 1)],
        unique=True,
        name="idx_invite_token_unique",
    )
    # TTL index: documentos expiram automaticamente apos expires_at
    coll.create_index(
        [("expires_at", 1)],
        expireAfterSeconds=0,
        name="idx_invite_ttl",
    )
    # Busca por tenant+email (verificar convite duplicado)
    coll.create_index(
        [("tenant_id", 1), ("email", 1)],
        name="idx_invite_tenant_email",
    )
    print("  kanban_invite_tokens: 3 indices")

    print(f"\nTotal: 15 indices criados/verificados.")


if __name__ == "__main__":
    print("=== Kanban: Setup Indexes ===\n")
    setup_indexes()
    print("\nDone.")
