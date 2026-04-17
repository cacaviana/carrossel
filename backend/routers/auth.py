"""Router do dominio Auth — camada opaca, sem logica.

Recebe DTO, delega para Service, retorna response.
NUNCA acessa campos do DTO diretamente.
"""

from fastapi import APIRouter, Depends, Request

from dtos.auth.login.request import LoginRequest
from dtos.auth.login.response import LoginResponse
from dtos.auth.me.response import MeResponse
from dtos.auth.criar_usuario.request import CriarUsuarioRequest
from dtos.auth.criar_usuario.response import UsuarioResponse
from dtos.auth.convidar_usuario.request import ConvidarUsuarioRequest
from dtos.auth.convidar_usuario.response import ConviteResponse
from dtos.auth.aceitar_convite.request import AceitarConviteRequest
from dtos.auth.atualizar_usuario.request import AtualizarUsuarioRequest
from dtos.auth.listar_usuarios.response import ListarUsuariosResponse
from middleware.auth import get_current_user, require_role, CurrentUser
from middleware.rate_limiter import limiter
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticacao"])


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(request: Request, dto: LoginRequest):
    """Login com email + senha. Rate limit: 5/min."""
    return AuthService.login(dto)


@router.get("/me", response_model=MeResponse)
async def me(current_user: CurrentUser = Depends(get_current_user)):
    """Retorna dados do usuario autenticado."""
    return AuthService.me(current_user)


@router.post("/users", response_model=UsuarioResponse, status_code=201)
async def criar_usuario(
    dto: CriarUsuarioRequest,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """Cria usuario diretamente (admin only)."""
    return AuthService.criar_usuario(dto, current_user)


@router.get("/users", response_model=ListarUsuariosResponse)
async def listar_usuarios(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Lista usuarios ativos do tenant."""
    return AuthService.listar_usuarios(current_user)


@router.post("/users/invite", response_model=ConviteResponse, status_code=201)
async def convidar_usuario(
    request: Request,
    dto: ConvidarUsuarioRequest,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """Convida usuario por email (admin only). Gera token com 48h de validade."""
    base_url = str(request.base_url).rstrip("/")
    return AuthService.convidar_usuario(dto, current_user, base_url)


@router.post("/users/invite/accept", response_model=LoginResponse, status_code=201)
async def aceitar_convite(dto: AceitarConviteRequest):
    """Aceita convite, cria usuario com senha e ja retorna JWT (auto-login). Endpoint publico."""
    return AuthService.aceitar_convite(dto)


@router.patch("/users/{user_id}", response_model=UsuarioResponse)
async def atualizar_usuario(
    user_id: str,
    dto: AtualizarUsuarioRequest,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """Atualiza dados de um usuario (admin only)."""
    return AuthService.atualizar_usuario(user_id, dto, current_user)


@router.delete("/users/{user_id}")
async def desativar_usuario(
    user_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """Soft delete de usuario (admin only)."""
    return AuthService.desativar_usuario(user_id, current_user)


@router.post("/users/{user_id}/reativar", response_model=UsuarioResponse)
async def reativar_usuario(
    user_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """Reativa usuario desativado (admin only)."""
    return AuthService.reativar_usuario(user_id, current_user)
