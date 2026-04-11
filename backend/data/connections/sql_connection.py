from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from config import settings

engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker | None = None


def _ensure_mars(url: str) -> str:
    """Garante que a conexao pyodbc tenha MARS_Connection=yes.

    Sem MARS, pyodbc + SQL Server lancam "Conexao ocupada com os resultados de
    outro comando" quando multiplas queries rodam na mesma sessao async
    (ex: loop de INSERTs em criar_pipeline).
    """
    parsed = urlparse(url)
    query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    # Pyodbc aceita MARS_Connection tanto com capitalizacoes diferentes
    if not any(k.lower() == "mars_connection" for k in query_params):
        query_params["MARS_Connection"] = "yes"
    new_query = urlencode(query_params)
    return urlunparse(parsed._replace(query=new_query))


def get_engine() -> AsyncEngine:
    global engine, AsyncSessionLocal
    if engine is None:
        if not settings.MSSQL_URL:
            raise RuntimeError("MSSQL_URL not configured in .env")
        engine = create_async_engine(
            _ensure_mars(settings.MSSQL_URL),
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
