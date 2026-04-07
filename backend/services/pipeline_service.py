import json as _json
from datetime import datetime, timezone

from dtos.pipeline.criar_pipeline.request import CriarPipelineRequest
from services.pipeline_db_service import (
    criar_pipeline,
    buscar_pipeline,
    listar_pipelines,
    buscar_etapa_por_agente,
    atualizar_etapa,
    atualizar_pipeline,
    buscar_proxima_etapa,
)
from services.pipeline_executor import executar_proxima_etapa


class PipelineService:
    @staticmethod
    async def criar(dto: CriarPipelineRequest) -> dict:
        formato = dto.get_formato()
        slides_pronto = None
        if dto.slides_texto_pronto:
            slides_pronto = [s.model_dump() for s in dto.slides_texto_pronto]
        result = await criar_pipeline(
            dto.tema, formato, dto.modo_funil,
            modo_entrada=dto.modo_entrada,
            slides_texto_pronto=slides_pronto,
            brand_slug=dto.brand_slug,
            avatar_mode=dto.avatar_mode or "livre",
        )
        return result

    @staticmethod
    async def buscar_etapa(pipeline_id: str, agente: str) -> dict:
        step = await buscar_etapa_por_agente(pipeline_id, agente)
        if not step:
            return None

        saida = step.get("saida")
        entrada = step.get("entrada")
        if isinstance(saida, str):
            try:
                saida = _json.loads(saida)
            except (ValueError, TypeError):
                pass
        if isinstance(entrada, str):
            try:
                entrada = _json.loads(entrada)
            except (ValueError, TypeError):
                pass

        pipeline_data = await buscar_pipeline(pipeline_id)
        tema = pipeline_data["tema"] if pipeline_data else ""
        formato = pipeline_data["formato"] if pipeline_data else ""

        # Limpar backgrounds base64 pesados (nao precisam ir pro frontend)
        if agente == "image_generator" and isinstance(saida, dict):
            for versao in saida.get("versoes", []):
                versao.pop("background_base64", None)

        # Progresso em tempo real (para etapas longas como image_generator)
        from services.step_progress import buscar as buscar_progresso
        progresso = buscar_progresso(str(step["id"]))

        result = {
            "id": str(step["id"]),
            "pipeline_id": pipeline_id,
            "agente": step["agente"],
            "status": step["status"],
            "entrada": {**(entrada or {}), "tema": tema, "formato": formato},
            "saida": saida or {},
        }
        if progresso:
            result["progresso"] = progresso
        return result

    @staticmethod
    async def buscar(pipeline_id: str) -> dict | None:
        return await buscar_pipeline(pipeline_id)

    @staticmethod
    async def listar(formato: str | None = None, status: str | None = None, limit: int = 50) -> dict:
        items = await listar_pipelines(limit=limit)
        if formato:
            items = [i for i in items if i["formato"] == formato]
        if status:
            items = [i for i in items if i["status"] == status]
        return {"items": items, "total": len(items)}

    @staticmethod
    async def executar(pipeline_id: str) -> dict:
        return await executar_proxima_etapa(pipeline_id)

    @staticmethod
    async def aprovar_etapa(pipeline_id: str, agente: str, saida_editada: str | None) -> dict:
        step = await buscar_etapa_por_agente(pipeline_id, agente)
        if not step:
            return None

        if step["status"] != "aguardando_aprovacao":
            raise ValueError(
                f"Etapa '{agente}' nao esta aguardando aprovacao (status: {step['status']})"
            )

        step_id = str(step["id"])
        now = datetime.now(timezone.utc)

        updates = {
            "status": "aprovado",
            "approved_at": now,
        }

        if saida_editada is not None:
            updates["saida"] = saida_editada

        await atualizar_etapa(step_id, updates)

        _, proxima = await buscar_proxima_etapa(pipeline_id)
        if proxima:
            await atualizar_pipeline(pipeline_id, {"status": "pendente"})
        else:
            await atualizar_pipeline(pipeline_id, {"status": "completo"})

        return {
            "pipeline_id": pipeline_id,
            "etapa": agente,
            "status": "aprovado",
            "mensagem": f"Etapa '{agente}' aprovada com sucesso",
        }

    @staticmethod
    async def rejeitar_etapa(pipeline_id: str, agente: str, motivo: str) -> dict:
        step = await buscar_etapa_por_agente(pipeline_id, agente)
        if not step:
            return None

        if step["status"] not in ("aguardando_aprovacao", "completo"):
            raise ValueError(
                f"Etapa '{agente}' nao pode ser rejeitada (status: {step['status']})"
            )

        step_id = str(step["id"])
        now = datetime.now(timezone.utc)

        await atualizar_etapa(step_id, {
            "status": "rejeitado",
            "erro_mensagem": motivo or "Rejeitado pelo usuario",
            "finished_at": now,
        })

        await atualizar_pipeline(pipeline_id, {
            "status": "pendente",
            "etapa_atual": agente,
        })

        return {
            "pipeline_id": pipeline_id,
            "etapa": agente,
            "status": "rejeitado",
            "mensagem": f"Etapa '{agente}' rejeitada. Execute novamente para re-processar.",
        }

    @staticmethod
    async def cancelar(pipeline_id: str) -> dict:
        result = await buscar_pipeline(pipeline_id)
        if not result:
            return None

        if result["status"] in ("completo", "cancelado"):
            raise ValueError(f"Pipeline ja esta {result['status']}")

        await atualizar_pipeline(pipeline_id, {"status": "cancelado"})
        return {"pipeline_id": pipeline_id, "status": "cancelado", "mensagem": "Pipeline cancelado"}

    @staticmethod
    async def retomar(pipeline_id: str) -> dict:
        result = await buscar_pipeline(pipeline_id)
        if not result:
            return None

        if result["status"] not in ("cancelado", "erro"):
            raise ValueError("Apenas pipelines cancelados ou com erro podem ser retomados")

        await atualizar_pipeline(pipeline_id, {"status": "pendente"})
        return {"pipeline_id": pipeline_id, "status": "pendente", "mensagem": "Pipeline retomado"}
