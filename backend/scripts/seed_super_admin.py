"""Seed do super_admin da plataforma.

Cria o tenant raiz 'plataforma' + o usuario super_admin que gerencia tenants.
Idempotente: se ja existir, so avisa e sai.

Uso:
    cd backend
    python scripts/seed_super_admin.py
    python scripts/seed_super_admin.py --email sa@minhaplataforma.com --password "MinhaSenha1!"
"""

import argparse
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.connections.mongo_connection import get_mongo_db

try:
    from middleware.auth import hash_password
except ImportError:
    from passlib.context import CryptContext
    _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    def hash_password(password: str) -> str:
        return _pwd_context.hash(password)


PLATAFORMA_TENANT_ID = "plataforma"
DEFAULT_EMAIL = "super@plataforma.com"
DEFAULT_NAME = "Super Admin"
DEFAULT_PASSWORD = "SuperAdmin@123"


def seed(email: str, name: str, password: str):
    db = get_mongo_db()
    if db is None:
        print("ERRO: MONGO_URL nao configurado.")
        sys.exit(1)

    # Garante tenant "plataforma" (onde o super_admin vive)
    if not db.tenants.find_one({"tenant_id": PLATAFORMA_TENANT_ID}):
        db.tenants.insert_one({
            "tenant_id": PLATAFORMA_TENANT_ID,
            "nome": "Plataforma",
            "plano": "enterprise",
            "status": "ativo",
            "limites": {"creditos_mes": 999999, "marcas_max": 999},
            "branding_default": {
                "paleta_fundo": "#0A0A0A", "paleta_texto": "#FAFAFA",
                "paleta_destaque": "#A78BFA", "fonte": "Outfit",
            },
            "admin_user_id": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
            "created_by": "seed",
            "audit_log": [],
        })
        print(f"  Tenant '{PLATAFORMA_TENANT_ID}' criado")
    else:
        print(f"  Tenant '{PLATAFORMA_TENANT_ID}' ja existe")

    # Super admin user
    existing = db.kanban_users.find_one({
        "tenant_id": PLATAFORMA_TENANT_ID,
        "email": email.lower(),
    })
    if existing:
        print(f"  Super admin '{email}' ja existe. Nada a fazer.")
        return

    doc = {
        "tenant_id": PLATAFORMA_TENANT_ID,
        "email": email.lower(),
        "name": name,
        "avatar_url": None,
        "password_hash": hash_password(password),
        "role": "super_admin",
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
        "deleted_at": None,
    }
    result = db.kanban_users.insert_one(doc)
    print(f"  Super admin criado: id={result.inserted_id}")
    print(f"  Email: {email}")
    print(f"  Senha: {password}")
    print(f"  Tenant: {PLATAFORMA_TENANT_ID}")
    print(f"  Role: super_admin")
    print()
    print(f"  Login: POST /api/auth/login com {{email, password}}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed do super_admin da plataforma")
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--name", default=DEFAULT_NAME)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    args = parser.parse_args()
    seed(args.email, args.name, args.password)
