"""Executa todos os scripts de setup do Kanban na ordem correta.

Ordem:
  1. kanban_setup_collections.py  — cria collections com validators
  2. kanban_setup_indexes.py      — cria indices otimizados
  3. kanban_seed_board.py         — board padrao com 6 colunas
  4. kanban_seed_admin.py         — usuario admin inicial

Uso:
    cd backend
    python scripts/kanban_run_all.py
    python scripts/kanban_run_all.py --tenant meu-tenant
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import direto das funcoes de cada script
from scripts.kanban_setup_collections import setup_collections
from scripts.kanban_setup_indexes import setup_indexes
from scripts.kanban_seed_board import seed_board
from scripts.kanban_seed_admin import seed_admin, DEFAULT_TENANT_ID, DEFAULT_EMAIL, DEFAULT_NAME, DEFAULT_PASSWORD


def run_all(tenant_id: str, email: str, name: str, password: str):
    print("=" * 60)
    print("  KANBAN MONGODB SETUP — EXECUCAO COMPLETA")
    print("=" * 60)

    print("\n[1/4] Criando collections com validators...")
    setup_collections()

    print("\n[2/4] Criando indices...")
    setup_indexes()

    print(f"\n[3/4] Seed do board padrao (tenant: {tenant_id})...")
    seed_board(tenant_id)

    print(f"\n[4/4] Seed do admin (email: {email})...")
    seed_admin(tenant_id, email, name, password)

    print("\n" + "=" * 60)
    print("  SETUP COMPLETO!")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup completo do Kanban no MongoDB")
    parser.add_argument("--tenant", default=DEFAULT_TENANT_ID)
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--name", default=DEFAULT_NAME)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    args = parser.parse_args()

    run_all(args.tenant, args.email, args.name, args.password)
