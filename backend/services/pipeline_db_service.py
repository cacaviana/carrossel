import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import text

from config import settings
from data.connections.database import get_sql_session_context


ETAPAS_PIPELINE = [
    ("strategist", 1),
    ("copywriter", 2),
    ("art_director", 3),
    ("image_generator", 4),
    ("brand_gate", 5),
    ("content_critic", 6),
]

FORMATOS_SLIDE_UNICO = ("post_unico", "thumbnail_youtube", "capa_reels")


async def criar_pipeline(tema, formato, modo_funil, tenant_id="itvalley", modo_entrada="ideia", slides_texto_pronto=None, brand_slug=None, avatar_mode="livre"):
    if not settings.MSSQL_URL:
        return None
    async with get_sql_session_context() as session:
        pipeline_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        is_texto_pronto = modo_entrada == "texto_pronto"
        etapa_inicial = "art_director" if is_texto_pronto else "strategist"

        await session.execute(
            text("""INSERT INTO carrossel.pipeline
            (id, tenant_id, tema, formato, modo_funil, status, etapa_atual, created_at, brand_slug, avatar_mode)
            VALUES (:id, :tenant_id, :tema, :formato, :modo_funil, :status, :etapa_atual, :created_at, :brand_slug, :avatar_mode)"""),
            {
                "id": pipeline_id,
                "tenant_id": tenant_id,
                "tema": tema,
                "formato": formato,
                "modo_funil": 1 if modo_funil else 0,
                "status": "pendente",
                "etapa_atual": etapa_inicial,
                "created_at": now,
                "brand_slug": brand_slug,
                "avatar_mode": avatar_mode,
            },
        )

        for agente, ordem in ETAPAS_PIPELINE:
            step_id = str(uuid.uuid4())

            if is_texto_pronto and agente == "strategist":
                briefing_json = json.dumps({
                    "briefing": {
                        "tema_principal": tema,
                        "angulo": "Conteudo fornecido pelo usuario — transformar em visual",
                        "publico_alvo": "Desenvolvedores e profissionais de tecnologia",
                        "objetivo": "Informar e engajar",
                        "tom": "Tecnico mas acessivel. Estilo IT Valley.",
                        "palavras_chave": [],
                        "referencias": [],
                    },
                    "funil": [{
                        "titulo": tema[:80],
                        "etapa_funil": "meio",
                        "formato": formato,
                        "resumo": "Conteudo fornecido diretamente pelo usuario",
                    }],
                }, ensure_ascii=False)
                await session.execute(
                    text("""INSERT INTO carrossel.pipeline_step
                    (id, pipeline_id, agente, ordem, status, entrada, saida, created_at, started_at, finished_at)
                    VALUES (:id, :pipeline_id, :agente, :ordem, :status, :entrada, :saida, :created_at, :started_at, :finished_at)"""),
                    {
                        "id": step_id,
                        "pipeline_id": pipeline_id,
                        "agente": agente,
                        "ordem": ordem,
                        "status": "aprovado",
                        "entrada": json.dumps({"tema": tema}, ensure_ascii=False),
                        "saida": briefing_json,
                        "created_at": now,
                        "started_at": now,
                        "finished_at": now,
                    },
                )
            elif is_texto_pronto and agente == "copywriter":
                slides_para_copy = []
                for idx, s in enumerate(slides_texto_pronto or []):
                    tipo = "capa" if idx == 0 else ("cta" if idx == len(slides_texto_pronto or []) - 1 else "conteudo")
                    slides_para_copy.append({
                        "indice": idx + 1,
                        "tipo": tipo,
                        "titulo": s.get("principal", "") if isinstance(s, dict) else s.principal,
                        "corpo": s.get("alternativo", "") if isinstance(s, dict) else s.alternativo,
                        "notas": "Texto fornecido pelo usuario — NAO reescrever",
                    })
                copy_json = json.dumps({
                    "headline": tema,
                    "narrativa": "Conteudo original do usuario — texto pronto",
                    "cta": (slides_para_copy[-1]["titulo"] if slides_para_copy else ""),
                    "slides": slides_para_copy,
                    "legenda_linkedin": "",
                    "hashtags": [],
                }, ensure_ascii=False)
                await session.execute(
                    text("""INSERT INTO carrossel.pipeline_step
                    (id, pipeline_id, agente, ordem, status, entrada, saida, created_at, started_at, finished_at)
                    VALUES (:id, :pipeline_id, :agente, :ordem, :status, :entrada, :saida, :created_at, :started_at, :finished_at)"""),
                    {
                        "id": step_id,
                        "pipeline_id": pipeline_id,
                        "agente": agente,
                        "ordem": ordem,
                        "status": "aprovado",
                        "entrada": json.dumps({"texto_pronto": True}, ensure_ascii=False),
                        "saida": copy_json,
                        "created_at": now,
                        "started_at": now,
                        "finished_at": now,
                    },
                )
            else:
                await session.execute(
                    text("""INSERT INTO carrossel.pipeline_step
                    (id, pipeline_id, agente, ordem, status, created_at)
                    VALUES (:id, :pipeline_id, :agente, :ordem, :status, :created_at)"""),
                    {
                        "id": step_id,
                        "pipeline_id": pipeline_id,
                        "agente": agente,
                        "ordem": ordem,
                        "status": "pendente",
                        "created_at": now,
                    },
                )

        return {
            "id": pipeline_id,
            "tema": tema,
            "formato": formato,
            "modo_funil": modo_funil,
            "modo_entrada": modo_entrada,
            "brand_slug": brand_slug,
            "avatar_mode": avatar_mode,
            "status": "pendente",
            "etapa_atual": etapa_inicial,
            "created_at": now.isoformat(),
        }


async def buscar_pipeline(pipeline_id, tenant_id="itvalley"):
    if not settings.MSSQL_URL:
        return None
    async with get_sql_session_context() as session:
        result = await session.execute(
            text("SELECT * FROM carrossel.pipeline WHERE id = :id AND tenant_id = :tenant_id AND deleted_at IS NULL"),
            {"id": pipeline_id, "tenant_id": tenant_id},
        )
        pipeline = result.mappings().first()
        if not pipeline:
            return None

        result2 = await session.execute(
            text("SELECT id, agente, ordem, status, started_at, finished_at FROM carrossel.pipeline_step WHERE pipeline_id = :pipeline_id ORDER BY ordem"),
            {"pipeline_id": pipeline_id},
        )
        steps = result2.mappings().all()

        from services.step_progress import buscar as buscar_progresso

        etapas_list = []
        for s in steps:
            step_dict = {
                "id": str(s["id"]),
                "agente": s["agente"],
                "ordem": s["ordem"],
                "status": s["status"],
                "started_at": s["started_at"].isoformat() if s.get("started_at") else None,
                "finished_at": s["finished_at"].isoformat() if s.get("finished_at") else None,
            }
            prog = buscar_progresso(str(s["id"]))
            if prog:
                step_dict["progresso"] = prog
            etapas_list.append(step_dict)

        return {
            "id": str(pipeline["id"]),
            "tema": pipeline["tema"],
            "formato": pipeline["formato"],
            "modo_funil": bool(pipeline["modo_funil"]),
            "status": pipeline["status"],
            "etapa_atual": pipeline["etapa_atual"],
            "brand_slug": pipeline.get("brand_slug"),
            "avatar_mode": pipeline.get("avatar_mode", "livre"),
            "created_at": pipeline["created_at"].isoformat() if pipeline["created_at"] else None,
            "etapas": etapas_list,
        }


async def listar_pipelines(tenant_id="itvalley", limit=50):
    if not settings.MSSQL_URL:
        return []
    async with get_sql_session_context() as session:
        result = await session.execute(
            text(f"SELECT TOP {limit} * FROM carrossel.pipeline WHERE tenant_id = :tenant_id AND deleted_at IS NULL ORDER BY created_at DESC"),
            {"tenant_id": tenant_id},
        )
        rows = result.mappings().all()
        return [
            {
                "id": str(r["id"]),
                "tema": r["tema"],
                "formato": r["formato"],
                "status": r["status"],
                "etapa_atual": r["etapa_atual"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
            for r in rows
        ]


async def buscar_proxima_etapa(pipeline_id, tenant_id="itvalley"):
    if not settings.MSSQL_URL:
        return None, None
    async with get_sql_session_context() as session:
        result = await session.execute(
            text("SELECT * FROM carrossel.pipeline WHERE id = :id AND tenant_id = :tenant_id AND deleted_at IS NULL"),
            {"id": pipeline_id, "tenant_id": tenant_id},
        )
        pipeline = result.mappings().first()
        if not pipeline:
            return None, None

        result2 = await session.execute(
            text("""SELECT TOP 1 * FROM carrossel.pipeline_step
            WHERE pipeline_id = :pipeline_id AND status = 'executando'"""),
            {"pipeline_id": pipeline_id},
        )
        if result2.mappings().first():
            return pipeline, None

        result3 = await session.execute(
            text("""SELECT TOP 1 * FROM carrossel.pipeline_step
            WHERE pipeline_id = :pipeline_id AND status IN ('pendente', 'rejeitado')
            ORDER BY ordem ASC"""),
            {"pipeline_id": pipeline_id},
        )
        step = result3.mappings().first()
        return pipeline, step


async def buscar_etapa_por_agente(pipeline_id, agente):
    if not settings.MSSQL_URL:
        return None
    async with get_sql_session_context() as session:
        result = await session.execute(
            text("SELECT * FROM carrossel.pipeline_step WHERE pipeline_id = :pipeline_id AND agente = :agente"),
            {"pipeline_id": pipeline_id, "agente": agente},
        )
        return result.mappings().first()


async def buscar_etapas_anteriores(pipeline_id, ordem_atual):
    if not settings.MSSQL_URL:
        return []
    async with get_sql_session_context() as session:
        result = await session.execute(
            text("""SELECT * FROM carrossel.pipeline_step
            WHERE pipeline_id = :pipeline_id AND ordem < :ordem_atual
            ORDER BY ordem ASC"""),
            {"pipeline_id": pipeline_id, "ordem_atual": ordem_atual},
        )
        return result.mappings().all()


async def atualizar_etapa(step_id, updates: dict):
    if not settings.MSSQL_URL:
        return
    async with get_sql_session_context() as session:
        set_clauses = []
        params = {"step_id": step_id}
        for i, (key, val) in enumerate(updates.items()):
            param_name = f"p{i}"
            set_clauses.append(f"{key} = :{param_name}")
            params[param_name] = val
        sql = f"UPDATE carrossel.pipeline_step SET {', '.join(set_clauses)} WHERE id = :step_id"
        await session.execute(text(sql), params)


async def atualizar_pipeline(pipeline_id, updates: dict):
    if not settings.MSSQL_URL:
        return
    async with get_sql_session_context() as session:
        set_clauses = []
        params = {"pipeline_id": pipeline_id}
        for i, (key, val) in enumerate(updates.items()):
            param_name = f"p{i}"
            set_clauses.append(f"{key} = :{param_name}")
            params[param_name] = val
        sql = f"UPDATE carrossel.pipeline SET {', '.join(set_clauses)} WHERE id = :pipeline_id"
        await session.execute(text(sql), params)
