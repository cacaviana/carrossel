from contextlib import asynccontextmanager

from data.connections.sql_connection import get_session_factory


async def get_sql_session():
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_sql_session_context():
    """Async context manager for use outside FastAPI Depends."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
