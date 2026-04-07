from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

from models.base import Base, TenantMixin


class ConteudoModel(TenantMixin, Base):
    __tablename__ = "conteudo"
    __table_args__ = {"schema": "carrossel"}

    pipeline_id = Column(UNIQUEIDENTIFIER, ForeignKey("carrossel.pipeline.id"), nullable=True)
    formato = Column(String(50), nullable=False)
    titulo = Column(String(500), nullable=False)
    headline = Column(Text, nullable=True)
    narrativa = Column(Text, nullable=True)
    hook = Column(Text, nullable=True)
    cta = Column(Text, nullable=True)
    copy_completa = Column(Text, nullable=True)
    legenda_linkedin = Column(Text, nullable=True)
    disciplina = Column(String(50), nullable=True)
    tecnologia_principal = Column(String(100), nullable=True)
