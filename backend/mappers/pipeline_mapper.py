import json

from models.pipeline import PipelineModel, PipelineStepModel
from dtos.pipeline.criar_pipeline.response import CriarPipelineResponse
from dtos.pipeline.buscar_pipeline.response import BuscarPipelineResponse, BuscarEtapaDetalhe
from dtos.pipeline.listar_pipelines.response import PipelineResumo
from dtos.pipeline.buscar_etapa.response import BuscarEtapaResponse
from dtos.pipeline.base import EtapaBase


class PipelineMapper:

    @staticmethod
    def to_criar_response(model: PipelineModel) -> CriarPipelineResponse:
        etapas = [
            EtapaBase(
                agente=e.agente,
                ordem=e.ordem,
                status=e.status,
            )
            for e in sorted(model.etapas, key=lambda e: e.ordem)
        ]
        return CriarPipelineResponse(
            id=model.id,
            tema=model.tema,
            formato=model.formato,
            modo_funil=model.modo_funil,
            status=model.status,
            etapa_atual=model.etapa_atual,
            etapas=etapas,
            created_at=model.created_at,
        )

    @staticmethod
    def to_buscar_response(model: PipelineModel) -> BuscarPipelineResponse:
        etapas = [
            BuscarEtapaDetalhe(
                id=e.id,
                agente=e.agente,
                ordem=e.ordem,
                status=e.status,
                erro_mensagem=e.erro_mensagem,
                started_at=e.started_at,
                finished_at=e.finished_at,
                entrada_resumo=PipelineMapper._resumir_json(e.entrada),
                saida_resumo=PipelineMapper._resumir_json(e.saida),
                aprovado_por=e.aprovado_por,
                approved_at=e.approved_at,
            )
            for e in sorted(model.etapas, key=lambda e: e.ordem)
        ]
        return BuscarPipelineResponse(
            id=model.id,
            tema=model.tema,
            formato=model.formato,
            modo_funil=model.modo_funil,
            status=model.status,
            etapa_atual=model.etapa_atual,
            modo_entrada=model.modo_entrada,
            disciplina=model.disciplina,
            tecnologia=model.tecnologia,
            etapas=etapas,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_resumo(model: PipelineModel) -> PipelineResumo:
        return PipelineResumo(
            id=model.id,
            tema=model.tema,
            formato=model.formato,
            status=model.status,
            etapa_atual=model.etapa_atual,
            created_at=model.created_at,
        )

    @staticmethod
    def to_list_resumo(models: list[PipelineModel]) -> list[PipelineResumo]:
        return [PipelineMapper.to_resumo(m) for m in models]

    @staticmethod
    def to_etapa_response(step: PipelineStepModel) -> BuscarEtapaResponse:
        return BuscarEtapaResponse(
            id=step.id,
            agente=step.agente,
            ordem=step.ordem,
            status=step.status,
            entrada=json.loads(step.entrada) if step.entrada else None,
            saida=json.loads(step.saida) if step.saida else None,
            erro_mensagem=step.erro_mensagem,
            aprovado_por=step.aprovado_por,
            approved_at=step.approved_at,
            started_at=step.started_at,
            finished_at=step.finished_at,
        )

    @staticmethod
    def _resumir_json(text: str | None) -> str | None:
        if not text:
            return None
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                keys = list(data.keys())[:5]
                return f"{{ {', '.join(keys)}... }}"
            return str(data)[:200]
        except (json.JSONDecodeError, TypeError):
            return text[:200] if text else None
