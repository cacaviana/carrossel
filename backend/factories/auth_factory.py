"""Factory do dominio Auth — criacao de objetos + regras de negocio.

Responsabilidades:
- Validar login (senha correta, usuario ativo)
- Criar documento de usuario com hash
- Criar documento de convite com token + TTL
"""

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from middleware.auth import hash_password, verify_password


class AuthFactory:
    """Cria e valida objetos do dominio Auth."""

    VALID_ROLES = {"admin", "copywriter", "designer", "reviewer", "viewer"}

    @staticmethod
    def validate_login(email: str, password: str, user_doc: dict | None) -> dict:
        """Valida credenciais de login.

        Regras:
        - Usuario deve existir
        - Usuario nao pode estar soft-deleted
        - Senha deve conferir com hash

        Returns: user_doc validado
        Raises: HTTPException 401 se invalido
        """
        if user_doc is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha invalidos",
            )

        if user_doc.get("deleted_at") is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario desativado. Contate o administrador.",
            )

        if not verify_password(password, user_doc.get("password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha invalidos",
            )

        return user_doc

    @staticmethod
    def create_user_doc(dto, tenant_id: str) -> dict:
        """Cria documento MongoDB de usuario a partir do DTO.

        Regras:
        - Senha hasheada com bcrypt
        - Role deve ser valido
        - email em lowercase
        """
        return {
            "tenant_id": tenant_id,
            "email": dto.email.lower(),
            "name": dto.name,
            "avatar_url": getattr(dto, "avatar_url", None),
            "password_hash": hash_password(dto.password),
            "role": dto.role,
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
            "deleted_at": None,
        }

    @staticmethod
    def create_invite_doc(dto, tenant_id: str, created_by: str) -> dict:
        """Cria documento de convite com token seguro.

        Regras:
        - Token gerado com secrets.token_urlsafe(32)
        - Expira em 48h (TTL index no MongoDB apaga automaticamente)
        """
        return {
            "tenant_id": tenant_id,
            "email": dto.email.lower(),
            "name": dto.name,
            "role": dto.role,
            "token": secrets.token_urlsafe(32),
            "created_by": created_by,
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=48),
            "used": False,
            "created_at": datetime.now(timezone.utc),
        }

    @staticmethod
    def create_user_from_invite(invite_doc: dict, password: str) -> dict:
        """Cria documento de usuario a partir de um convite aceito.

        Regras:
        - Convite nao pode estar usado
        - Convite nao pode estar expirado
        - Senha hasheada com bcrypt
        """
        if invite_doc.get("used"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Convite ja utilizado",
            )

        if invite_doc.get("expires_at") and invite_doc["expires_at"] < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Convite expirado",
            )

        return {
            "tenant_id": invite_doc["tenant_id"],
            "email": invite_doc["email"].lower(),
            "name": invite_doc["name"],
            "avatar_url": None,
            "password_hash": hash_password(password),
            "role": invite_doc["role"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
            "deleted_at": None,
        }

    @staticmethod
    def build_update_fields(dto) -> dict:
        """Constroi dict de campos para update a partir do DTO.

        So inclui campos que nao sao None (partial update).
        """
        updates = {}
        if dto.name is not None:
            updates["name"] = dto.name
        if dto.role is not None:
            updates["role"] = dto.role
        if dto.avatar_url is not None:
            updates["avatar_url"] = dto.avatar_url
        if updates:
            updates["updated_at"] = datetime.now(timezone.utc)
        return updates
