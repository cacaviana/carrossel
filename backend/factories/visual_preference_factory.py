import json
import uuid
from datetime import datetime, timezone

from models.visual_preference import VisualPreferenceModel
from dtos.visual_preference.salvar_preferencia.request import SalvarPreferenciaRequest


class VisualPreferenceFactory:

    @staticmethod
    def to_model(dto: SalvarPreferenciaRequest, tenant_id: str) -> VisualPreferenceModel:
        if not dto.estilo or not dto.estilo.strip():
            raise ValueError("Estilo obrigatorio")

        return VisualPreferenceModel(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            estilo=dto.estilo.strip(),
            aprovado=dto.aprovado,
            contexto=json.dumps(dto.contexto) if dto.contexto else None,
            created_at=datetime.now(timezone.utc),
        )
