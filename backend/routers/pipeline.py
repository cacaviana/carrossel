from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from dtos.pipeline.criar_pipeline.request import CriarPipelineRequest
from dtos.pipeline.aprovar_etapa.request import AprovarEtapaRequest
from dtos.pipeline.rejeitar_etapa.request import RejeitarEtapaRequest
from middleware.rate_limiter import limiter
from services.pipeline_service import PipelineService

router = APIRouter(prefix="/pipelines", tags=["Pipeline"])


@router.post("/", status_code=201)
async def criar(dto: CriarPipelineRequest):
    try:
        return await PipelineService.criar(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pipeline_id}/etapas/{agente}")
async def buscar_etapa(pipeline_id: str, agente: str):
    """Retorna os dados de uma etapa especifica (entrada, saida, status)."""
    result = await PipelineService.buscar_etapa(pipeline_id, agente)
    if not result:
        raise HTTPException(status_code=404, detail=f"Etapa '{agente}' nao encontrada")
    return result


@router.get("/{pipeline_id}")
async def buscar(pipeline_id: str):
    result = await PipelineService.buscar(pipeline_id)
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline nao encontrado")
    return result


@router.get("/")
async def listar(formato: str | None = None, status: str | None = None, limit: int = 50):
    return await PipelineService.listar(formato=formato, status=status, limit=limit)


@router.post("/{pipeline_id}/executar")
@limiter.limit("15/minute")
async def executar(request: Request, pipeline_id: str):
    """Executa a proxima etapa pendente do pipeline."""
    try:
        return await PipelineService.executar(pipeline_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao executar etapa: {str(e)}")


@router.post("/{pipeline_id}/etapas/{agente}/aprovar")
async def aprovar_etapa(pipeline_id: str, agente: str, dto: AprovarEtapaRequest):
    """Aprova uma etapa do pipeline. Opcionalmente aceita saida editada."""
    try:
        result = await PipelineService.aprovar_etapa(pipeline_id, agente, dto.saida_editada)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail=f"Etapa '{agente}' nao encontrada")
    return result


@router.post("/{pipeline_id}/etapas/{agente}/rejeitar")
async def rejeitar_etapa(pipeline_id: str, agente: str, dto: RejeitarEtapaRequest):
    """Rejeita uma etapa do pipeline. Permite re-execucao."""
    try:
        result = await PipelineService.rejeitar_etapa(pipeline_id, agente, dto.motivo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail=f"Etapa '{agente}' nao encontrada")
    return result


@router.post("/{pipeline_id}/cancelar")
async def cancelar_pipeline(pipeline_id: str):
    """Cancela um pipeline em andamento."""
    try:
        result = await PipelineService.cancelar(pipeline_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline nao encontrado")
    return result


@router.get("/{pipeline_id}/imagens/{slide_index}")
async def servir_imagem_pipeline(pipeline_id: str, slide_index: int):
    """Serve imagem de slide direto do disco (PNG)."""
    from utils.pipeline_images import caminho_absoluto
    path_rel = f"pipeline-images/{pipeline_id}/slide-{slide_index:02d}.png"
    path = caminho_absoluto(path_rel)
    if not path:
        raise HTTPException(status_code=404, detail="Imagem nao encontrada")
    return FileResponse(path, media_type="image/png")


@router.post("/{pipeline_id}/retomar")
async def retomar_pipeline(pipeline_id: str):
    """Retoma um pipeline cancelado ou com erro."""
    try:
        result = await PipelineService.retomar(pipeline_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline nao encontrado")
    return result
