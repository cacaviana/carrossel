from models.historico import HistoricoModel
from dtos.historico.listar_historico.response import HistoricoItem
from dtos.historico.buscar_historico.response import BuscarHistoricoResponse


class HistoricoMapper:

    @staticmethod
    def to_item(model: HistoricoModel) -> HistoricoItem:
        return HistoricoItem(
            id=model.id,
            titulo=model.titulo,
            formato=model.formato,
            status=model.status,
            disciplina=model.disciplina,
            tecnologia_principal=model.tecnologia_principal,
            tipo_carrossel=model.tipo_carrossel,
            total_slides=model.total_slides,
            final_score=model.final_score,
            google_drive_link=model.google_drive_link,
            google_drive_folder_name=model.google_drive_folder_name,
            pipeline_id=model.pipeline_id,
            created_at=model.created_at,
        )

    @staticmethod
    def to_list(models: list[HistoricoModel]) -> list[HistoricoItem]:
        return [HistoricoMapper.to_item(m) for m in models]

    @staticmethod
    def to_buscar_response(model: HistoricoModel) -> BuscarHistoricoResponse:
        return BuscarHistoricoResponse(
            id=model.id,
            titulo=model.titulo,
            formato=model.formato,
            status=model.status,
            disciplina=model.disciplina,
            tecnologia_principal=model.tecnologia_principal,
            tipo_carrossel=model.tipo_carrossel,
            total_slides=model.total_slides,
            final_score=model.final_score,
            legenda_linkedin=model.legenda_linkedin,
            google_drive_link=model.google_drive_link,
            google_drive_folder_name=model.google_drive_folder_name,
            pipeline_id=model.pipeline_id,
            created_at=model.created_at,
        )
