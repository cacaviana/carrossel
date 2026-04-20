"""Router do dominio Tenant.

Endpoints:
- POST   /api/tenants            criar (super_admin)
- GET    /api/tenants/me         obter tenant atual (qualquer autenticado)
- GET    /api/tenants            listar (super_admin)
- PATCH  /api/tenants/{tenant_id} atualizar (super_admin ou admin do proprio tenant)

Camada opaca: so delega pro TenantService e retorna DTO.
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from middleware.auth import CurrentUser, get_current_user, require_role
from services.tenant_service import TenantService

from dtos.tenant.criar_tenant.request import CriarTenantRequest
from dtos.tenant.criar_tenant.response import CriarTenantResponse
from dtos.tenant.obter_tenant_atual.response import ObterTenantAtualResponse
from dtos.tenant.listar_tenants.response import ListarTenantsResponse
from dtos.tenant.atualizar_tenant.request import AtualizarTenantRequest
from dtos.tenant.atualizar_tenant.response import AtualizarTenantResponse


router = APIRouter(prefix="/tenants", tags=["Tenant"])


@router.post("", response_model=CriarTenantResponse, status_code=201)
async def criar_tenant(
    dto: CriarTenantRequest,
    current_user: CurrentUser = Depends(require_role("super_admin")),
):
    return TenantService.criar(dto, created_by=current_user.user_id)


@router.get("/me", response_model=ObterTenantAtualResponse)
async def obter_tenant_atual(
    current_user: CurrentUser = Depends(get_current_user),
):
    return TenantService.obter_atual(tenant_id=current_user.tenant_id)


@router.get("", response_model=ListarTenantsResponse)
async def listar_tenants(
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: str | None = Query(None, description="ativo | inativo"),
    current_user: CurrentUser = Depends(require_role("super_admin")),
):
    return TenantService.listar(limit=limit, offset=offset, status_filter=status)


@router.patch("/{tenant_id}", response_model=AtualizarTenantResponse)
async def atualizar_tenant(
    tenant_id: str,
    dto: AtualizarTenantRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    # super_admin atualiza qualquer; admin so o proprio.
    if current_user.role != "super_admin":
        if current_user.role != "admin" or current_user.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Sem permissao para atualizar este tenant")
    return TenantService.atualizar(tenant_id, dto, updated_by=current_user.user_id)
