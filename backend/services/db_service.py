import os
import asyncio

import pymssql


def _get_conn():
    url = os.getenv("MSSQL_URL", "")
    # Parse: mssql+aioodbc://user:pass@host/db?...
    if "://" in url:
        rest = url.split("://", 1)[1]
        userpass, hostdb = rest.split("@", 1)
        user, password = userpass.split(":", 1)
        host, db_and_params = hostdb.split("/", 1)
        db = db_and_params.split("?", 1)[0]
    else:
        raise ValueError("MSSQL_URL não configurada")
    return pymssql.connect(server=host, user=user, password=password, database=db, port=1433)


def _salvar_sync(titulo, disciplina, tecnologia, tipo, total_slides, legenda, drive_link, folder_name):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO carrossel.historico
        (titulo, disciplina, tecnologia_principal, tipo_carrossel, total_slides, legenda_linkedin, google_drive_link, google_drive_folder_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (titulo, disciplina, tecnologia, tipo, total_slides, legenda, drive_link, folder_name),
    )
    conn.commit()
    conn.close()


def _listar_sync(limit=50):
    conn = _get_conn()
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        f"SELECT TOP {limit} * FROM carrossel.historico ORDER BY criado_em DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
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
        })
    return result


def _deletar_sync(item_id):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carrossel.historico WHERE id = %s", (item_id,))
    conn.commit()
    conn.close()


async def salvar_historico(titulo, disciplina, tecnologia, tipo, total_slides, legenda, drive_link, folder_name):
    await asyncio.get_event_loop().run_in_executor(
        None, _salvar_sync, titulo, disciplina, tecnologia, tipo, total_slides, legenda, drive_link, folder_name
    )


async def listar_historico(limit=50):
    return await asyncio.get_event_loop().run_in_executor(None, _listar_sync, limit)


async def deletar_historico(item_id):
    await asyncio.get_event_loop().run_in_executor(None, _deletar_sync, item_id)
