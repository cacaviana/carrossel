from sqlalchemy import Column, String, Integer, Text, Float

from models.base import Base, TenantMixin


class HistoricoModel(TenantMixin, Base):
    __tablename__ = "historico"
    __table_args__ = {"schema": "carrossel"}

    titulo = Column(String(500), nullable=False)
    formato = Column(String(50), nullable=True, default="carrossel")
    status = Column(String(30), nullable=True, default="completo")
    disciplina = Column(String(50), nullable=True)
    tecnologia_principal = Column(String(100), nullable=True)
    tipo_carrossel = Column(String(30), nullable=True)
    total_slides = Column(Integer, nullable=True)
    final_score = Column(Float, nullable=True)
    legenda_linkedin = Column(Text, nullable=True)
    google_drive_link = Column(Text, nullable=True)
    google_drive_folder_name = Column(String(500), nullable=True)
    pipeline_id = Column(String(36), nullable=True)
