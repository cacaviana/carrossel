from sqlalchemy import Column, String, Boolean, Text

from models.base import Base, TenantMixin


class VisualPreferenceModel(TenantMixin, Base):
    __tablename__ = "visual_preference"
    __table_args__ = {"schema": "carrossel"}

    estilo = Column(String(200), nullable=False)
    aprovado = Column(Boolean, nullable=False)
    contexto = Column(Text, nullable=True)
