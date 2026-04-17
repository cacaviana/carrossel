from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse

from dtos.pipeline.criar_pipeline.request import CriarPipelineRequest
from dtos.pipeline.aprovar_etapa.request import AprovarEtapaRequest
from dtos.pipeline.rejeitar_etapa.request import RejeitarEtapaRequest
from middleware.auth import CurrentUser, get_current_user
from middleware.rate_limiter import limiter
from services.pipeline_service import PipelineService

router = APIRouter(prefix="/pipelines", tags=["Pipeline"])


@router.post("/", status_code=201)
async def criar(
    dto: CriarPipelineRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    try:
        return await PipelineService.criar(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pipeline_id}/etapas/{agente}")
async def buscar_etapa(
    pipeline_id: str,
    agente: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retorna os dados de uma etapa especifica (entrada, saida, status)."""
    result = await PipelineService.buscar_etapa(pipeline_id, agente)
    if not result:
        raise HTTPException(status_code=404, detail=f"Etapa '{agente}' nao encontrada")
    return result


@router.get("/{pipeline_id}")
async def buscar(
    pipeline_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    result = await PipelineService.buscar(pipeline_id)
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline nao encontrado")
    return result


@router.get("/")
async def listar(
    formato: str | None = None,
    status: str | None = None,
    limit: int = 50,
    current_user: CurrentUser = Depends(get_current_user),
):
    return await PipelineService.listar(formato=formato, status=status, limit=limit)


@router.post("/{pipeline_id}/executar")
@limiter.limit("15/minute")
async def executar(
    request: Request,
    pipeline_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
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
async def aprovar_etapa(
    pipeline_id: str,
    agente: str,
    dto: AprovarEtapaRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Aprova uma etapa do pipeline. Opcionalmente aceita saida editada.

    Aceita dois formatos de body (backward-compatible):
    - Legado: {saida_editada: str}
    - Frontend novo: {dados_editados: dict, etapa: str}
    """
    try:
        result = await PipelineService.aprovar_etapa(
            pipeline_id,
            agente,
            saida_editada=dto.saida_editada,
            dados_editados=dto.dados_editados,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail=f"Etapa '{agente}' nao encontrada")
    return result


@router.post("/{pipeline_id}/etapas/{agente}/rejeitar")
async def rejeitar_etapa(
    pipeline_id: str,
    agente: str,
    dto: RejeitarEtapaRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Rejeita uma etapa do pipeline. Permite re-execucao."""
    try:
        result = await PipelineService.rejeitar_etapa(pipeline_id, agente, dto.motivo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail=f"Etapa '{agente}' nao encontrada")
    return result


@router.post("/{pipeline_id}/cancelar")
async def cancelar_pipeline(
    pipeline_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Cancela um pipeline em andamento."""
    try:
        result = await PipelineService.cancelar(pipeline_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline nao encontrado")
    return result


@router.get("/{pipeline_id}/imagens/{slide_index}")
async def servir_imagem_pipeline(
    pipeline_id: str,
    slide_index: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Serve imagem de slide direto do disco (PNG)."""
    from utils.pipeline_images import caminho_absoluto
    path_rel = f"pipeline-images/{pipeline_id}/slide-{slide_index:02d}.png"
    path = caminho_absoluto(path_rel)
    if not path:
        raise HTTPException(status_code=404, detail="Imagem nao encontrada")
    return FileResponse(path, media_type="image/png")


@router.get("/{pipeline_id}/imagens")
async def listar_imagens_pipeline(
    pipeline_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Lista imagens disponíveis no disco para o pipeline."""
    from pathlib import Path
    from utils.pipeline_images import IMAGES_DIR
    pipeline_dir = IMAGES_DIR / pipeline_id
    if not pipeline_dir.exists():
        return {"imagens": []}
    imagens = []
    for f in sorted(pipeline_dir.glob("slide-*.png")):
        idx = int(f.stem.replace("slide-", ""))
        imagens.append({
            "slide_index": idx,
            "variacao": 1,
            "image_path": f"pipeline-images/{pipeline_id}/{f.name}",
            "image_url": f"/api/pipelines/{pipeline_id}/imagens/{idx}",
        })
    return {"imagens": imagens, "total_slides": len(imagens)}


@router.post("/{pipeline_id}/regerar-imagens")
async def regerar_imagens(
    pipeline_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Reseta art_director + image_generator + brand_gate + content_critic
    mantendo strategist + copywriter aprovados. Util pra testar prompts de imagem."""
    from services.pipeline_db_service import buscar_pipeline, atualizar_etapa, atualizar_pipeline

    pipeline = await buscar_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline nao encontrado")

    ETAPAS_A_RESETAR = ("art_director", "image_generator", "brand_gate", "content_critic")

    for step in pipeline.get("etapas", []):
        if step["agente"] in ETAPAS_A_RESETAR:
            await atualizar_etapa(str(step["id"]), {
                "status": "pendente",
                "saida": None,
                "entrada": None,
                "erro_mensagem": None,
                "started_at": None,
                "finished_at": None,
            })

    await atualizar_pipeline(pipeline_id, {
        "status": "aguardando_aprovacao",
        "etapa_atual": "art_director",
    })

    return {"pipeline_id": pipeline_id, "resetadas": list(ETAPAS_A_RESETAR), "mensagem": "Execute o pipeline para regerar imagens"}


@router.post("/{pipeline_id}/retomar")
async def retomar_pipeline(
    pipeline_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retoma um pipeline cancelado ou com erro."""
    try:
        result = await PipelineService.retomar(pipeline_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline nao encontrado")
    return result
