"""Cria as 7 collections do Kanban com JSON Schema validation no MongoDB.

Database: content_factory (mesmo do sistema existente).
Executar uma unica vez. Idempotente (verifica se collection ja existe).

Uso:
    cd backend
    python scripts/kanban_setup_collections.py
"""

import os
import sys
from datetime import datetime, timezone

# Adiciona backend/ ao path para imports do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.connections.mongo_connection import get_mongo_db


# ---------------------------------------------------------------------------
# 1. kanban_users
# ---------------------------------------------------------------------------
KANBAN_USERS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["tenant_id", "email", "name", "password_hash", "role", "created_at"],
        "properties": {
            "tenant_id": {
                "bsonType": "string",
                "description": "ID do tenant — obrigatorio em toda collection",
            },
            "email": {
                "bsonType": "string",
                "description": "Email do usuario, unico por tenant",
            },
            "name": {
                "bsonType": "string",
                "minLength": 2,
                "description": "Nome do usuario",
            },
            "avatar_url": {
                "bsonType": ["string", "null"],
                "description": "URL do avatar (opcional)",
            },
            "password_hash": {
                "bsonType": "string",
                "description": "Hash bcrypt da senha",
            },
            "role": {
                "bsonType": "string",
                "enum": ["admin", "copywriter", "designer", "reviewer", "viewer"],
                "description": "Perfil ACL do usuario",
            },
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": ["date", "null"]},
            "deleted_at": {"bsonType": ["date", "null"], "description": "Soft delete"},
        },
    }
}

# ---------------------------------------------------------------------------
# 2. kanban_boards
# ---------------------------------------------------------------------------
KANBAN_BOARDS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["tenant_id", "name", "columns", "created_at"],
        "properties": {
            "tenant_id": {"bsonType": "string"},
            "name": {"bsonType": "string"},
            "columns": {
                "bsonType": "array",
                "description": "Colunas do board como subdocumento",
                "items": {
                    "bsonType": "object",
                    "required": ["id", "name", "order"],
                    "properties": {
                        "id": {"bsonType": "string", "description": "ID fixo da coluna"},
                        "name": {"bsonType": "string"},
                        "order": {"bsonType": "int"},
                        "color": {"bsonType": ["string", "null"]},
                        "auto_assign_user_ids": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"},
                            "description": "Pos-MVP: auto-assign ao mover card pra coluna",
                        },
                    },
                },
            },
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": ["date", "null"]},
        },
    }
}

# ---------------------------------------------------------------------------
# 3. kanban_cards
# ---------------------------------------------------------------------------
KANBAN_CARDS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "tenant_id", "board_id", "column_id", "title",
            "priority", "created_by", "created_at",
        ],
        "properties": {
            "tenant_id": {"bsonType": "string"},
            "board_id": {"bsonType": "string"},
            "column_id": {"bsonType": "string"},
            "title": {"bsonType": "string", "minLength": 1},
            "copy_text": {"bsonType": ["string", "null"]},
            "disciplina": {"bsonType": ["string", "null"]},
            "tecnologia": {"bsonType": ["string", "null"]},
            "priority": {
                "bsonType": "string",
                "enum": ["alta", "media", "baixa"],
                "description": "Default: media (RN-014)",
            },
            "assigned_user_ids": {
                "bsonType": "array",
                "items": {"bsonType": "string"},
            },
            "created_by": {"bsonType": "string", "description": "user_id do criador"},
            "pipeline_id": {"bsonType": ["string", "null"]},
            "drive_link": {"bsonType": ["string", "null"]},
            "drive_folder_name": {"bsonType": ["string", "null"]},
            "pdf_url": {"bsonType": ["string", "null"]},
            "image_urls": {
                "bsonType": "array",
                "items": {"bsonType": "string"},
            },
            "order_in_column": {"bsonType": "int"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": ["date", "null"]},
            "archived_at": {"bsonType": ["date", "null"], "description": "Soft delete"},
        },
    }
}

# ---------------------------------------------------------------------------
# 4. kanban_comments
# ---------------------------------------------------------------------------
KANBAN_COMMENTS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["tenant_id", "card_id", "user_id", "text", "created_at"],
        "properties": {
            "tenant_id": {"bsonType": "string"},
            "card_id": {"bsonType": "string"},
            "user_id": {"bsonType": "string"},
            "text": {"bsonType": "string", "minLength": 1},
            "parent_comment_id": {
                "bsonType": ["string", "null"],
                "description": "Thread 1 nivel (pos-MVP)",
            },
            "mentions": {
                "bsonType": "array",
                "items": {"bsonType": "string"},
                "description": "user_ids mencionados (pos-MVP)",
            },
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": ["date", "null"]},
            "deleted_at": {"bsonType": ["date", "null"]},
        },
    }
}

# ---------------------------------------------------------------------------
# 5. kanban_activity_log  (append-only — RN-013)
# ---------------------------------------------------------------------------
KANBAN_ACTIVITY_LOG_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["tenant_id", "card_id", "user_id", "action", "created_at"],
        "properties": {
            "tenant_id": {"bsonType": "string"},
            "card_id": {"bsonType": "string"},
            "user_id": {"bsonType": "string"},
            "action": {
                "bsonType": "string",
                "enum": [
                    "card_created",
                    "column_changed",
                    "assignee_changed",
                    "field_edited",
                    "comment_added",
                    "comment_edited",
                    "comment_deleted",
                    "image_generated",
                    "drive_linked",
                    "pdf_exported",
                ],
            },
            "metadata": {
                "bsonType": "object",
                "description": "Dados extras por tipo de acao (from_column, to_column, etc.)",
            },
            "created_at": {"bsonType": "date"},
        },
    }
}

# ---------------------------------------------------------------------------
# 6. kanban_notifications
# ---------------------------------------------------------------------------
KANBAN_NOTIFICATIONS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["tenant_id", "user_id", "card_id", "type", "message", "is_read", "created_at"],
        "properties": {
            "tenant_id": {"bsonType": "string"},
            "user_id": {"bsonType": "string", "description": "Destinatario"},
            "card_id": {"bsonType": "string"},
            "type": {
                "bsonType": "string",
                "enum": ["assigned", "mentioned", "column_changed"],
            },
            "message": {"bsonType": "string"},
            "is_read": {"bsonType": "bool"},
            "created_at": {"bsonType": "date"},
        },
    }
}

# ---------------------------------------------------------------------------
# 7. kanban_invite_tokens  (TTL 48h — expira automaticamente)
# ---------------------------------------------------------------------------
KANBAN_INVITE_TOKENS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["tenant_id", "email", "name", "role", "token", "created_by", "expires_at", "used", "created_at"],
        "properties": {
            "tenant_id": {"bsonType": "string"},
            "email": {"bsonType": "string"},
            "name": {"bsonType": "string"},
            "role": {
                "bsonType": "string",
                "enum": ["admin", "copywriter", "designer", "reviewer", "viewer"],
            },
            "token": {"bsonType": "string", "description": "secrets.token_urlsafe(32)"},
            "created_by": {"bsonType": "string", "description": "user_id do admin que convidou"},
            "expires_at": {"bsonType": "date", "description": "TTL index expira doc automaticamente"},
            "used": {"bsonType": "bool"},
            "created_at": {"bsonType": "date"},
        },
    }
}


# ---------------------------------------------------------------------------
# Mapa de collections e validators
# ---------------------------------------------------------------------------
COLLECTIONS = {
    "kanban_users": KANBAN_USERS_VALIDATOR,
    "kanban_boards": KANBAN_BOARDS_VALIDATOR,
    "kanban_cards": KANBAN_CARDS_VALIDATOR,
    "kanban_comments": KANBAN_COMMENTS_VALIDATOR,
    "kanban_activity_log": KANBAN_ACTIVITY_LOG_VALIDATOR,
    "kanban_notifications": KANBAN_NOTIFICATIONS_VALIDATOR,
    "kanban_invite_tokens": KANBAN_INVITE_TOKENS_VALIDATOR,
}


def setup_collections():
    """Cria as collections com validacao JSON Schema."""
    db = get_mongo_db()
    if db is None:
        print("ERRO: MONGO_URL nao configurado. Configure no .env e tente novamente.")
        sys.exit(1)

    existing = db.list_collection_names()

    for name, validator in COLLECTIONS.items():
        if name in existing:
            # Tenta atualizar validator (nao suportado em CosmosDB)
            try:
                db.command("collMod", name, validator=validator)
                print(f"  [UPDATE] {name} — validator atualizado")
            except Exception:
                print(f"  [SKIP]   {name} — ja existe (validator nao suportado neste backend)")
        else:
            try:
                db.create_collection(name, validator=validator)
                print(f"  [CREATE] {name} — collection criada com validator")
            except Exception:
                # CosmosDB: cria collection sem validator
                db.create_collection(name)
                print(f"  [CREATE] {name} — collection criada (sem validator, CosmosDB)")

    print(f"\n{len(COLLECTIONS)} collections configuradas no database 'content_factory'.")


if __name__ == "__main__":
    print("=== Kanban: Setup Collections ===\n")
    setup_collections()
    print("\nDone.")
