import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship

from models.base import Base, TenantMixin


class PipelineModel(TenantMixin, Base):
    __tablename__ = "pipeline"
    __table_args__ = {"schema": "carrossel"}

    tema = Column(Text, nullable=False)
    formato = Column(String(50), nullable=False)
    modo_funil = Column(Boolean, default=False)
    status = Column(String(30), nullable=False, default="pendente")
    etapa_atual = Column(String(50), nullable=True)
    modo_entrada = Column(String(20), nullable=True)
    disciplina = Column(String(50), nullable=True)
    tecnologia = Column(String(100), nullable=True)
    foto_criador = Column(Text, nullable=True)

    etapas = relationship("PipelineStepModel", back_populates="pipeline", cascade="all, delete-orphan")


class PipelineStepModel(Base):
    __tablename__ = "pipeline_step"
    __table_args__ = {"schema": "carrossel"}

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    pipeline_id = Column(UNIQUEIDENTIFIER, ForeignKey("carrossel.pipeline.id"), nullable=False)
    agente = Column(String(50), nullable=False)
    ordem = Column(Integer, nullable=False)
    entrada = Column(Text, nullable=True)
    saida = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="pendente")
    erro_mensagem = Column(Text, nullable=True)
    aprovado_por = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pipeline = relationship("PipelineModel", back_populates="etapas")
