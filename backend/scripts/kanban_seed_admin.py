"""Seed do usuario Admin inicial.

Cria o primeiro usuario admin para o tenant de desenvolvimento.
Senha padrao: Admin@123 (deve ser trocada apos primeiro login).

Uso:
    cd backend
    python scripts/kanban_seed_admin.py
    python scripts/kanban_seed_admin.py --email admin@itvalley.com --name "Carlos Viana" --password "Minha@Senha1"
"""

import argparse
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.connections.mongo_connection import get_mongo_db

# Importa hash_password do middleware que sera criado.
# Fallback para passlib direto se middleware ainda nao existir.
try:
    from middleware.auth import hash_password
except ImportError:
    from passlib.context import CryptContext
    _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    def hash_password(password: str) -> str:
        return _pwd_context.hash(password)


DEFAULT_TENANT_ID = "itvalley-dev"
DEFAULT_EMAIL = "admin@itvalley.com"
DEFAULT_NAME = "Admin IT Valley"
DEFAULT_PASSWORD = "Admin@123"  # Satisfaz RN-021: 8+ chars, maiuscula, numero, especial


def seed_admin(tenant_id: str, email: str, name: str, password: str):
    """Cria usuario admin se nao existir."""
    db = get_mongo_db()
    if db is None:
        print("ERRO: MONGO_URL nao configurado.")
        sys.exit(1)

    existing = db.kanban_users.find_one({
        "tenant_id": tenant_id,
        "email": email.lower(),
    })
    if existing:
        print(f"  Usuario '{email}' ja existe para tenant '{tenant_id}'. Nada a fazer.")
        return

    user = {
        "tenant_id": tenant_id,
        "email": email.lower(),
        "name": name,
        "avatar_url": None,
        "password_hash": hash_password(password),
        "role": "admin",
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
        "deleted_at": None,
    }

    result = db.kanban_users.insert_one(user)
    print(f"  Admin criado: id={result.inserted_id}")
    print(f"  Email: {email}")
    print(f"  Tenant: {tenant_id}")
    print(f"  Role: admin")
    print(f"  IMPORTANTE: Troque a senha padrao apos primeiro login!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed do usuario Admin do Kanban")
    parser.add_argument("--tenant", default=DEFAULT_TENANT_ID, help="ID do tenant")
    parser.add_argument("--email", default=DEFAULT_EMAIL, help="Email do admin")
    parser.add_argument("--name", default=DEFAULT_NAME, help="Nome do admin")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Senha inicial")
    args = parser.parse_args()

    print("=== Kanban: Seed Admin ===\n")
    seed_admin(args.tenant, args.email, args.name, args.password)
    print("\nDone.")
