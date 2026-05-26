"""Model SQLAlchemy do dominio Anuncio (pos-pivot 2026-04-23).

Anuncio = 1 formato 1080x1350 com copy de venda (headline + descricao + CTA).
Mesma dimensao do post_unico. Sem tabela filha de dimensoes.
"""
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Integer, Text, Float, ForeignKey, Index
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

from models.base import Base, TenantMixin
# Garante que o mapper do SQLAlchemy conheca a tabela-alvo da FK
from models.pipeline import PipelineModel  # noqa: F401


class AnuncioModel(TenantMixin, Base):
    """Anuncio 1080x1350 com copy de venda.

    Status:
      - rascunho: criado mas pipeline nao iniciou
      - gerando: pipeline em execucao
      - completo: imagem gerada + brand gate aprovado
      - erro: pipeline falhou (apos 2 retries)
      - cancelado: cancelado manualmente / soft deleted
    """
    __tablename__ = "anuncio"
    __table_args__ = (
        Index("ix_anuncio_tenant_status", "tenant_id", "status"),
        Index("ix_anuncio_tenant_pipeline", "tenant_id", "pipeline_id"),
        {"schema": "carrossel"},
    )

    pipeline_id = Column(
        UNIQUEIDENTIFIER,
        ForeignKey("carrossel.pipeline.id"),
        nullable=True,
    )
    pipeline_funil_id = Column(UNIQUEIDENTIFIER, nullable=True)

    titulo = Column(String(200), nullable=False)
    etapa_funil = Column(String(20), nullable=True)
    tema_ou_briefing = Column(Text, nullable=True)
    modo_entrada = Column(String(20), nullable=True)
    disciplina = Column(String(50), nullable=True)
    tecnologia = Column(String(100), nullable=True)
    foto_criador_id = Column(String(100), nullable=True)
    criado_por = Column(String(100), nullable=True)

    # Copy de venda (RN-017)
    headline = Column(String(40), nullable=True)        # max 40 chars
    descricao = Column(String(125), nullable=True)      # max 125 chars
    cta = Column(String(30), nullable=True)             # max 30 chars

    # Imagem final (1 unica)
    image_url = Column(String(2048), nullable=True)

    # Brand Gate
    brand_gate_score = Column(Float, nullable=True)
    brand_gate_feedback = Column(Text, nullable=True)
    tentativas = Column(Integer, nullable=False, default=0)

    status = Column(String(20), nullable=False, default="rascunho")
    drive_folder_id = Column(String(100), nullable=True)
    drive_folder_link = Column(Text, nullable=True)
    last_exported_at = Column(DateTime, nullable=True)
