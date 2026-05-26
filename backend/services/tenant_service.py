"""Service do dominio Tenant.

Orquestra: Factory → Repository → Mapper. Nao conhece campos (camada opaca).
"""

from fastapi import HTTPException, status

from factories.tenant_factory import TenantFactory
from factories.auth_factory import AuthFactory
from mappers.tenant_mapper import TenantMapper
from data.repositories.mongo.tenant_repository import TenantRepository
from data.repositories.mongo.auth_repository import AuthRepository


class TenantService:

    @staticmethod
    def criar(dto, created_by: str | None) -> dict:
        """Provisiona tenant + admin inicial. Idempotente por tenant_id (conflict se ja existir)."""
        if TenantRepository.exists(dto.tenant_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"tenant_id '{dto.tenant_id}' ja existe",
            )

        doc = TenantFactory.create_tenant_doc(dto, created_by=created_by)
        saved = TenantRepository.criar(doc)

        # Criar admin inicial no tenant recem-provisionado
        admin_doc = _build_admin_user_doc(
            email=dto.admin.email,
            nome=dto.admin.nome,
            senha=dto.admin.senha,
            tenant_id=dto.tenant_id,
        )
        admin = AuthRepository.insert_user(admin_doc)
        admin_user_id = str(admin["_id"])

        TenantRepository.atrelar_admin(dto.tenant_id, admin_user_id)

        return TenantMapper.to_criar_response(saved, admin_user_id, dto.admin.email.lower())

    @staticmethod
    def obter_atual(tenant_id: str) -> dict:
        doc = TenantRepository.find_by_tenant_id(tenant_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Tenant da sessao nao encontrado")
        return TenantMapper.to_obter_atual_response(doc)

    @staticmethod
    def listar(limit: int, offset: int, status_filter: str | None = None) -> dict:
        if status_filter:
            TenantFactory.validate_status(status_filter)
        docs, total = TenantRepository.listar(limit=limit, offset=offset, status=status_filter)
        return TenantMapper.to_listar_response(docs, total=total, limit=limit, offset=offset)

    @staticmethod
    def atualizar(tenant_id: str, dto, updated_by: str | None) -> dict:
        existing = TenantRepository.find_by_tenant_id(tenant_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Tenant nao encontrado")

        fields, audit_changes = TenantFactory.build_update_fields(dto, existing=existing)
        if not fields:
            raise HTTPException(status_code=400, detail="Nenhum campo valido para atualizar")

        audit_entry = TenantFactory.build_audit_entry(
            user_id=updated_by,
            action="tenant_updated",
            changes=audit_changes,
        )
        updated = TenantRepository.atualizar(tenant_id, fields, audit_entry=audit_entry)
        return TenantMapper.to_atualizar_response(updated, updated_by=updated_by)


def _build_admin_user_doc(email: str, nome: str, senha: str, tenant_id: str) -> dict:
    """Monta doc de usuario admin inicial do tenant. Reusa convencao do AuthFactory sem
    obrigar o DTO original (senha em texto plano → hash)."""
    from datetime import datetime, timezone
    from middleware.auth import hash_password

    return {
        "tenant_id": tenant_id,
        "email": email.lower(),
        "name": nome,
        "avatar_url": None,
        "password_hash": hash_password(senha),
        "role": "admin",
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
        "deleted_at": None,
    }
