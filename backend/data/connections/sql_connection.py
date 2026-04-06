from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from config import settings

engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker | None = None


def get_engine() -> AsyncEngine:
    global engine, AsyncSessionLocal
    if engine is None:
        if not settings.MSSQL_URL:
            raise RuntimeError("MSSQL_URL not configured in .env")
        engine = create_async_engine(
            settings.MSSQL_URL,
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600,
        )
        AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    return engine


def get_session_factory() -> async_sessionmaker:
    get_engine()
    return AsyncSessionLocal
