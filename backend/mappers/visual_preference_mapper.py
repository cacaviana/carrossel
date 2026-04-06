import json

from models.visual_preference import VisualPreferenceModel
from dtos.visual_preference.salvar_preferencia.response import SalvarPreferenciaResponse
from dtos.visual_preference.listar_preferencias.response import PreferenciaItem


class VisualPreferenceMapper:

    @staticmethod
    def to_salvar_response(model: VisualPreferenceModel) -> SalvarPreferenciaResponse:
        return SalvarPreferenciaResponse(
            id=model.id,
            estilo=model.estilo,
            aprovado=model.aprovado,
            created_at=model.created_at,
        )

    @staticmethod
    def to_item(model: VisualPreferenceModel) -> PreferenciaItem:
        contexto = None
        if model.contexto:
            try:
                contexto = json.loads(model.contexto)
            except (json.JSONDecodeError, TypeError):
                contexto = None
        return PreferenciaItem(
            id=model.id,
            estilo=model.estilo,
            aprovado=model.aprovado,
            contexto=contexto,
            created_at=model.created_at,
        )

    @staticmethod
    def to_list(models: list[VisualPreferenceModel]) -> list[PreferenciaItem]:
        return [VisualPreferenceMapper.to_item(m) for m in models]
