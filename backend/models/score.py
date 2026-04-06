from sqlalchemy import Column, Float, String, Text, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

from models.base import Base, TenantMixin


class ScoreModel(TenantMixin, Base):
    __tablename__ = "score"
    __table_args__ = {"schema": "carrossel"}

    conteudo_id = Column(UNIQUEIDENTIFIER, ForeignKey("carrossel.conteudo.id"), nullable=False)
    clarity = Column(Float, nullable=False)
    impact = Column(Float, nullable=False)
    originality = Column(Float, nullable=False)
    scroll_stop = Column(Float, nullable=False)
    cta_strength = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)
    decision = Column(String(30), nullable=False)
    best_variation = Column(String(10), nullable=True)
    feedback = Column(Text, nullable=True)
