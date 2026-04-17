"""Migration: adicionar coluna pipeline_id na tabela carrossel.historico.

Idempotente — se a coluna ja existir, nao faz nada.
"""
import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from sqlalchemy import text
from config import settings
from data.connections.database import get_sql_session_context


async def main():
    if not settings.MSSQL_URL:
        print("MSSQL_URL nao configurado")
        return
    async with get_sql_session_context() as session:
        existe = await session.execute(
            text("""SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = 'carrossel'
                      AND TABLE_NAME = 'historico'
                      AND COLUMN_NAME = 'pipeline_id'""")
        )
        if (existe.scalar() or 0) > 0:
            print("[skip] coluna pipeline_id ja existe em carrossel.historico")
            return

        await session.execute(
            text("ALTER TABLE carrossel.historico ADD pipeline_id UNIQUEIDENTIFIER NULL")
        )
        await session.commit()
        print("[ok] coluna pipeline_id adicionada em carrossel.historico")


if __name__ == "__main__":
    asyncio.run(main())
