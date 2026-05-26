from fastapi import APIRouter, Depends, HTTPException

from dtos.agentes.listar_agentes.response import AgenteResponse
from factories.agente_factory import AgenteFactory
from middleware.auth import CurrentUser, get_current_user

router = APIRouter()


@router.get("/agentes")
async def listar_agentes(
    current_user: CurrentUser = Depends(get_current_user),
) -> list[AgenteResponse]:
    agentes_llm, skills = AgenteFactory.listar_todos()
    result = []
    for meta in agentes_llm:
        result.append(AgenteResponse(
            slug=meta["slug"],
            nome=meta["nome"],
            descricao=meta["descricao"],
            tipo=meta["tipo"],
            conteudo=AgenteFactory.carregar_system_prompt(meta),
        ))
    for meta in skills:
        result.append(AgenteResponse(
            slug=meta["slug"],
            nome=meta["nome"],
            descricao=meta["descricao"],
            tipo=meta["tipo"],
            conteudo=AgenteFactory.carregar_system_prompt(meta),
        ))
    return result


@router.get("/agentes/{slug}")
async def buscar_agente(
    slug: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> AgenteResponse:
    meta = AgenteFactory.buscar_por_slug(slug)
    if not meta:
        raise HTTPException(status_code=404, detail="Agente nao encontrado")
    return AgenteResponse(
        slug=meta["slug"],
        nome=meta["nome"],
        descricao=meta["descricao"],
        tipo=meta["tipo"],
        conteudo=AgenteFactory.carregar_system_prompt(meta),
    )
