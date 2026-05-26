from fastapi import APIRouter, Depends, HTTPException

from dtos.design_system.salvar_design_system.request import DesignSystemRequest
from middleware.auth import CurrentUser, get_current_user
from skills.design_system_loader import listar, buscar, salvar, remover

router = APIRouter(prefix="/design-systems", tags=["Design Systems"])


@router.get("/")
async def api_listar(
    current_user: CurrentUser = Depends(get_current_user),
):
    return listar()


@router.get("/{slug}")
async def api_buscar(
    slug: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    ds = buscar(slug)
    if not ds:
        raise HTTPException(status_code=404, detail="Design system nao encontrado")
    return ds


@router.post("/", status_code=201)
async def api_salvar(
    req: DesignSystemRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    ds = req.model_dump()
    slug = salvar(ds)
    return {"slug": slug, "mensagem": f"Design system '{req.nome}' salvo"}


@router.put("/{slug}")
async def api_atualizar(
    slug: str,
    req: DesignSystemRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    existing = buscar(slug)
    if not existing:
        raise HTTPException(status_code=404, detail="Design system nao encontrado")
    ds = req.model_dump()
    ds["slug"] = slug
    salvar(ds)
    return {"slug": slug, "mensagem": f"Design system '{req.nome}' atualizado"}


@router.delete("/{slug}")
async def api_remover(
    slug: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    if not remover(slug):
        raise HTTPException(status_code=404, detail="Design system nao encontrado")
    return {"mensagem": f"Design system '{slug}' removido"}
