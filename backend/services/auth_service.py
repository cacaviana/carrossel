"""Service do dominio Auth — camada opaca.

Orquestra Factory, Mapper e Repository.
NUNCA acessa campos do DTO diretamente.
NUNCA acessa banco diretamente.
"""

import os

from fastapi import HTTPException, status

from data.repositories.mongo.auth_repository import AuthRepository
from data.repositories.mongo.invite_repository import InviteRepository
from factories.auth_factory import AuthFactory
from mappers.auth_mapper import AuthMapper
from middleware.auth import create_access_token, CurrentUser


# ---------------------------------------------------------------------------
# Tenant padrao — em producao vira do JWT; aqui fallback para dev
# ---------------------------------------------------------------------------
DEFAULT_TENANT_ID = os.getenv("DEFAULT_TENANT_ID", "itvalley-dev")


class AuthService:
    """Orquestra operacoes de autenticacao e gestao de usuarios."""

    @staticmethod
    def login(dto):
        """Autentica usuario e retorna JWT."""
        email, password = AuthFactory.extract_login_credentials(dto)
        user_doc = AuthRepository.find_by_email(DEFAULT_TENANT_ID, email)

        # Factory valida credenciais (regras de negocio)
        validated = AuthFactory.validate_login(email, password, user_doc)

        token = create_access_token({
            "user_id": str(validated["_id"]),
            "tenant_id": validated["tenant_id"],
            "role": validated["role"],
            "email": validated["email"],
            "name": validated["name"],
        })

        return AuthMapper.to_login_response(validated, token)

    @staticmethod
    def me(current_user: CurrentUser):
        """Retorna dados completos do usuario autenticado."""
        user_doc = AuthRepository.find_by_id(
            current_user.tenant_id,
            current_user.user_id,
        )
        if user_doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario nao encontrado",
            )
        return AuthMapper.to_me_response(user_doc)

    @staticmethod
    def criar_usuario(dto, current_user: CurrentUser):
        """Cria usuario diretamente (admin only)."""
        # Verifica email duplicado
        email = AuthFactory.extract_email(dto)
        if AuthRepository.email_exists(current_user.tenant_id, email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email ja cadastrado neste tenant",
            )

        # Factory cria documento com hash e regras
        doc = AuthFactory.create_user_doc(dto, current_user.tenant_id)
        saved = AuthRepository.insert_user(doc)
        return AuthMapper.to_usuario_response(saved)

    @staticmethod
    def listar_usuarios(current_user: CurrentUser):
        """Lista usuarios ativos do tenant."""
        docs = AuthRepository.find_all_by_tenant(current_user.tenant_id)
        return AuthMapper.to_listar_response(docs)

    @staticmethod
    def convidar_usuario(dto, current_user: CurrentUser, base_url: str):
        """Cria convite com token para novo usuario (admin only)."""
        # Verifica se email ja esta cadastrado
        email = AuthFactory.extract_email(dto)
        if AuthRepository.email_exists(current_user.tenant_id, email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email ja cadastrado neste tenant",
            )

        # Verifica se ja tem convite pendente
        pending = InviteRepository.find_pending_by_email(
            current_user.tenant_id,
            email,
        )
        if pending:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ja existe um convite pendente para este email",
            )

        # Factory cria documento de convite
        invite_doc = AuthFactory.create_invite_doc(
            dto, current_user.tenant_id, current_user.user_id,
        )
        saved = InviteRepository.insert_invite(invite_doc)
        return AuthMapper.to_convite_response(saved, base_url)

    @staticmethod
    def aceitar_convite(dto):
        """Aceita convite: cria usuario com a senha fornecida."""
        token, password = AuthFactory.extract_token_and_password(dto)
        invite_doc = InviteRepository.find_by_token(token)
        if invite_doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Convite nao encontrado ou expirado",
            )

        # Factory valida convite e cria usuario
        user_doc = AuthFactory.create_user_from_invite(invite_doc, password)

        # Verifica se email ja foi cadastrado (race condition guard)
        if AuthRepository.email_exists(user_doc["tenant_id"], user_doc["email"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email ja cadastrado neste tenant",
            )

        saved = AuthRepository.insert_user(user_doc)
        InviteRepository.mark_used(token)
        return AuthMapper.to_usuario_response(saved)

    @staticmethod
    def atualizar_usuario(user_id: str, dto, current_user: CurrentUser):
        """Atualiza dados de um usuario (admin only)."""
        # Factory constroi campos de update
        updates = AuthFactory.build_update_fields(dto)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum campo para atualizar",
            )

        updated = AuthRepository.update_user(
            current_user.tenant_id, user_id, updates,
        )
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario nao encontrado",
            )
        return AuthMapper.to_usuario_response(updated)

    @staticmethod
    def desativar_usuario(user_id: str, current_user: CurrentUser):
        """Soft delete de usuario (admin only)."""
        if user_id == current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nao e possivel desativar a si mesmo",
            )

        result = AuthRepository.soft_delete(
            current_user.tenant_id, user_id,
        )
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario nao encontrado",
            )
        return {"ok": True, "detail": "Usuario desativado"}

    @staticmethod
    def reativar_usuario(user_id: str, current_user: CurrentUser):
        """Reativa usuario soft-deleted (admin only)."""
        result = AuthRepository.reactivate(
            current_user.tenant_id, user_id,
        )
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario nao encontrado",
            )
        return AuthMapper.to_usuario_response(result)
