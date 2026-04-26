"""Integracao do dominio Anuncio com o pipeline de 6 agentes existente
(pos-pivot 2026-04-23).

Anuncio = 1 formato 1080x1350. Nao ha dimensoes. O pipeline roda o mesmo
fluxo de post_unico; a diferenca e que o Copywriter entra em modo 'venda'
e a imagem final e persistida na tabela anuncio (image_url, brand_gate_score,
tentativas).

Hook de wiring: `on_pipeline_completed(pipeline_id, tenant_id)` deve ser
chamado pelo pipeline_executor quando o pipeline de formato=anuncio termina
(status=completo ou status=erro).
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import text

from config import settings
from data.connections.database import get_sql_session_context
from factories.anuncio_factory import AnuncioFactory


ETAPAS_PIPELINE_ANUNCIO = [
    ("strategist", 1),
    ("copywriter", 2),
    ("art_director", 3),
    ("image_generator", 4),
    ("brand_gate", 5),
    ("content_critic", 6),
]


class AnuncioPipelineService:
    """Camada fina de cola Anuncio <-> Pipeline."""

    # ---------------- INICIAR PIPELINE ----------------
    @staticmethod
    async def iniciar_pipeline_anuncio(
        tema: str,
        modo_entrada: str,
        disciplina: Optional[str],
        tecnologia: Optional[str],
        foto_criador_id: Optional[str],
        etapa_funil: Optional[str],
        pipeline_funil_id: Optional[str],
        tenant_id: str,
        brand_slug: Optional[str] = None,
    ) -> str:
        """Cria uma linha em carrossel.pipeline com formato='anuncio' e
        retorna o pipeline_id (string).

        Se MSSQL nao estiver configurado, retorna um pipeline_id sintetico.
        """
        pipeline_id = str(uuid.uuid4())

        if not settings.MSSQL_URL:
            return pipeline_id

        async with get_sql_session_context() as session:
            now = datetime.now(timezone.utc)
            modo_funil = 1 if pipeline_funil_id else 0
            try:
                await session.execute(
                    text(
                        """INSERT INTO carrossel.pipeline
                        (id, tenant_id, tema, formato, modo_funil, status,
                         etapa_atual, created_at, modo_entrada, disciplina, tecnologia,
                         foto_criador, avatar_mode, brand_slug)
                        VALUES (:id, :tenant_id, :tema, :formato, :modo_funil, :status,
                                :etapa_atual, :created_at, :modo_entrada, :disciplina, :tecnologia,
                                :foto_criador, :avatar_mode, :brand_slug)"""
                    ),
                    {
                        "id": pipeline_id,
                        "tenant_id": tenant_id,
                        "tema": tema[:3000],
                        "formato": "anuncio",
                        "modo_funil": modo_funil,
                        "status": "pendente",
                        "etapa_atual": "strategist",
                        "created_at": now,
                        "modo_entrada": modo_entrada or "texto",
                        "disciplina": disciplina,
                        "tecnologia": tecnologia,
                        "foto_criador": foto_criador_id,
                        "avatar_mode": "livre",
                        "brand_slug": brand_slug,
                    },
                )
            except Exception:
                # Fallback pra schemas que nao tem brand_slug
                await session.execute(
                    text(
                        """INSERT INTO carrossel.pipeline
                        (id, tenant_id, tema, formato, modo_funil, status, etapa_atual, created_at)
                        VALUES (:id, :tenant_id, :tema, :formato, :modo_funil, :status, :etapa_atual, :created_at)"""
                    ),
                    {
                        "id": pipeline_id,
                        "tenant_id": tenant_id,
                        "tema": tema[:3000],
                        "formato": "anuncio",
                        "modo_funil": modo_funil,
                        "status": "pendente",
                        "etapa_atual": "strategist",
                        "created_at": now,
                    },
                )

            for agente, ordem in ETAPAS_PIPELINE_ANUNCIO:
                step_id = str(uuid.uuid4())
                try:
                    await session.execute(
                        text(
                            """INSERT INTO carrossel.pipeline_step
                            (id, pipeline_id, agente, ordem, status, created_at)
                            VALUES (:id, :pipeline_id, :agente, :ordem, :status, :created_at)"""
                        ),
                        {
                            "id": step_id,
                            "pipeline_id": pipeline_id,
                            "agente": agente,
                            "ordem": ordem,
                            "status": "pendente",
                            "created_at": now,
                        },
                    )
                except Exception:
                    break

        return pipeline_id

    # ---------------- REGENERAR IMAGEM ----------------
    @staticmethod
    async def regenerar_imagem(
        anuncio, tenant_id: str, feedback: Optional[str] = None,
    ) -> str:
        """Reinicia o pipeline pra regerar a imagem do anuncio existente.

        Reseta o pipeline anterior (drop steps) ou cria um novo pipeline
        -- aqui criamos um novo pipeline pra manter historico.

        Retorna o novo pipeline_id.
        """
        novo_pipeline_id = await AnuncioPipelineService.iniciar_pipeline_anuncio(
            tema=(anuncio.tema_ou_briefing or anuncio.titulo or "")[:3000],
            modo_entrada=anuncio.modo_entrada or "texto",
            disciplina=anuncio.disciplina,
            tecnologia=anuncio.tecnologia,
            foto_criador_id=anuncio.foto_criador_id,
            etapa_funil=anuncio.etapa_funil,
            pipeline_funil_id=str(anuncio.pipeline_funil_id) if anuncio.pipeline_funil_id else None,
            tenant_id=tenant_id,
            brand_slug=None,
        )
        anuncio.pipeline_id = novo_pipeline_id
        if feedback:
            anuncio.brand_gate_feedback = feedback[:3000]
        AnuncioFactory.marcar_gerando(anuncio)
        return novo_pipeline_id

    # ---------------- HOOK: PIPELINE CONCLUIDO ----------------
    @staticmethod
    async def on_pipeline_completed(
        pipeline_id: str, tenant_id: str, image_url: Optional[str] = None,
        saidas_agentes: Optional[dict] = None,
    ) -> None:
        """Hook chamado pelo pipeline_executor quando um pipeline formato=anuncio
        termina. Popula image_url, copy e status=completo no AnuncioModel.

        saidas_agentes: dict {"copywriter": {...}, "image_generator": {...}, ...}
        image_url: URL/data URI da imagem final (se fornecida).
        """
        if not settings.MSSQL_URL:
            return

        from data.repositories.sql.anuncio_repository import AnuncioRepository

        async with get_sql_session_context() as session:
            repo = AnuncioRepository(session)
            anuncio = await repo.get_by_pipeline_id(pipeline_id, tenant_id)
            if not anuncio:
                return  # pipeline nao associado a anuncio (pode ser outro formato)

            # Extrai copy do saidas_agentes (copywriter) se disponivel
            saidas = saidas_agentes or {}
            copy_out = saidas.get("copywriter") or {}
            headline = copy_out.get("headline")
            descricao = copy_out.get("descricao")
            cta = copy_out.get("cta")

            # Brand gate score (se aplicavel)
            brand_gate_out = saidas.get("brand_gate") or {}
            score = brand_gate_out.get("score") or brand_gate_out.get("brand_gate_score")

            # Contador de tentativas (cada vez que passa por este hook +1)
            novas_tentativas = int(anuncio.tentativas or 0) + 1

            AnuncioFactory.registrar_pipeline_concluido(
                anuncio=anuncio,
                image_url=image_url or "",
                headline=headline,
                descricao=descricao,
                cta=cta,
                brand_gate_score=score,
                tentativas=novas_tentativas,
            )
            await repo.update(anuncio)

    @staticmethod
    async def on_pipeline_erro(
        pipeline_id: str, tenant_id: str, feedback: str = "",
    ) -> None:
        """Hook chamado quando pipeline formato=anuncio falha."""
        if not settings.MSSQL_URL:
            return

        from data.repositories.sql.anuncio_repository import AnuncioRepository

        async with get_sql_session_context() as session:
            repo = AnuncioRepository(session)
            anuncio = await repo.get_by_pipeline_id(pipeline_id, tenant_id)
            if not anuncio:
                return

            novas_tentativas = int(anuncio.tentativas or 0) + 1
            AnuncioFactory.registrar_pipeline_erro(
                anuncio=anuncio, feedback=feedback, tentativas=novas_tentativas,
            )
            await repo.update(anuncio)
