from sqlalchemy import text

from config import settings
from data.connections.database import get_sql_session_context


async def salvar_historico(titulo, disciplina, tecnologia, tipo, total_slides, legenda, drive_link, folder_name):
    if not settings.MSSQL_URL:
        return
    async with get_sql_session_context() as session:
        await session.execute(
            text("""INSERT INTO carrossel.historico
            (titulo, disciplina, tecnologia_principal, tipo_carrossel, total_slides, legenda_linkedin, google_drive_link, google_drive_folder_name)
            VALUES (:titulo, :disciplina, :tecnologia, :tipo, :total_slides, :legenda, :drive_link, :folder_name)"""),
            {
                "titulo": titulo,
                "disciplina": disciplina,
                "tecnologia": tecnologia,
                "tipo": tipo,
                "total_slides": total_slides,
                "legenda": legenda,
                "drive_link": drive_link,
                "folder_name": folder_name,
            },
        )


async def listar_historico(limit=50):
    if not settings.MSSQL_URL:
        return []
    async with get_sql_session_context() as session:
        result = await session.execute(
            text(f"SELECT TOP {limit} * FROM carrossel.historico ORDER BY criado_em DESC")
        )
        rows = result.mappings().all()
        return [
            {
                "id": r["id"],
                "titulo": r["titulo"],
                "disciplina": r["disciplina"],
                "tecnologia_principal": r["tecnologia_principal"],
                "tipo_carrossel": r["tipo_carrossel"],
                "total_slides": r["total_slides"],
                "legenda_linkedin": r["legenda_linkedin"],
                "google_drive_link": r["google_drive_link"],
                "google_drive_folder_name": r["google_drive_folder_name"],
                "criado_em": r["criado_em"].isoformat() if r["criado_em"] else None,
            }
            for r in rows
        ]


async def deletar_historico(item_id):
    if not settings.MSSQL_URL:
        return
    async with get_sql_session_context() as session:
        await session.execute(
            text("DELETE FROM carrossel.historico WHERE id = :item_id"),
            {"item_id": item_id},
        )
