import uuid
from datetime import datetime, timezone

from models.historico import HistoricoModel


class HistoricoFactory:

    @staticmethod
    def to_model(
        titulo: str,
        tenant_id: str,
        formato: str = "carrossel",
        status: str = "completo",
        disciplina: str | None = None,
        tecnologia_principal: str | None = None,
        tipo_carrossel: str | None = None,
        total_slides: int | None = None,
        final_score: float | None = None,
        legenda_linkedin: str | None = None,
        google_drive_link: str | None = None,
        google_drive_folder_name: str | None = None,
        pipeline_id: str | None = None,
    ) -> HistoricoModel:
        if not titulo or not titulo.strip():
            raise ValueError("Titulo obrigatorio")

        return HistoricoModel(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            titulo=titulo.strip(),
            formato=formato,
            status=status,
            disciplina=disciplina,
            tecnologia_principal=tecnologia_principal,
            tipo_carrossel=tipo_carrossel,
            total_slides=total_slides,
            final_score=final_score,
            legenda_linkedin=legenda_linkedin,
            google_drive_link=google_drive_link,
            google_drive_folder_name=google_drive_folder_name,
            pipeline_id=pipeline_id,
            created_at=datetime.now(timezone.utc),
        )
