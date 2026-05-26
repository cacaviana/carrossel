from sqlalchemy import Column, String, Text, Integer, Boolean, Float, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

from models.base import Base, TenantMixin


class ImagemModel(TenantMixin, Base):
    __tablename__ = "imagem"
    __table_args__ = {"schema": "carrossel"}

    conteudo_id = Column(UNIQUEIDENTIFIER, ForeignKey("carrossel.conteudo.id"), nullable=False)
    slide_index = Column(Integer, nullable=False)
    variacao = Column(Integer, nullable=False)
    url_drive = Column(Text, nullable=True)
    image_base64 = Column(Text, nullable=True)
    modelo_gemini = Column(String(50), nullable=True)
    brand_gate_status = Column(String(30), nullable=True)
    brand_gate_retries = Column(Integer, default=0)
    selecionada = Column(Boolean, default=False)
