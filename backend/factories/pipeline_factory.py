import uuid
from datetime import datetime, timezone

from models.pipeline import PipelineModel, PipelineStepModel
from dtos.pipeline.criar_pipeline.request import CriarPipelineRequest


# Ordem fixa das etapas do pipeline
ETAPAS_PIPELINE = [
    ("strategist", 1),
    ("copywriter", 2),
    ("hook_specialist", 3),
    ("art_director", 4),
    ("image_generator", 5),
    ("brand_gate", 6),
    ("content_critic", 7),
]

# Etapas que exigem aprovacao humana
ETAPAS_APROVACAO = {
    "strategist": "AP-1",
    "hook_specialist": "AP-2",
    "art_director": "AP-3",
    "brand_gate": "AP-4",
}

FORMATOS_VALIDOS = ["carrossel", "post_unico", "thumbnail_youtube"]


class PipelineFactory:

    @staticmethod
    def to_model(dto: CriarPipelineRequest, tenant_id: str) -> PipelineModel:
        formato = dto.get_formato()
        if formato not in FORMATOS_VALIDOS:
            raise ValueError(f"Formato invalido: {formato}. Validos: {FORMATOS_VALIDOS}")

        if dto.modo_entrada != "texto_pronto" and len(dto.tema.strip()) < 20:
            raise ValueError("Tema deve ter no minimo 20 caracteres")

        if dto.modo_entrada == "disciplina" and not dto.disciplina:
            raise ValueError("Disciplina obrigatoria quando modo_entrada = disciplina")

        pipeline_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        pipeline = PipelineModel(
            id=pipeline_id,
            tenant_id=tenant_id,
            tema=dto.tema.strip(),
            formato=formato,
            modo_funil=dto.modo_funil,
            status="pendente",
            etapa_atual="strategist",
            modo_entrada=dto.modo_entrada,
            disciplina=dto.disciplina,
            tecnologia=dto.tecnologia,
            foto_criador=dto.foto_criador,
            created_at=now,
        )

        pipeline.etapas = []
        for agente, ordem in ETAPAS_PIPELINE:
            step = PipelineStepModel(
                id=uuid.uuid4(),
                pipeline_id=pipeline_id,
                agente=agente,
                ordem=ordem,
                status="pendente",
                created_at=now,
            )
            pipeline.etapas.append(step)

        return pipeline

    @staticmethod
    def etapa_requer_aprovacao(agente: str) -> bool:
        return agente in ETAPAS_APROVACAO

    @staticmethod
    def proxima_etapa(etapa_atual: str) -> str | None:
        for agente, ordem in ETAPAS_PIPELINE:
            if agente == etapa_atual:
                for next_agente, next_ordem in ETAPAS_PIPELINE:
                    if next_ordem == ordem + 1:
                        return next_agente
                return None
        return None
