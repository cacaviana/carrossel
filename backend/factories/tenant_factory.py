"""Factory do dominio Tenant — criacao de objetos + regras de negocio."""

from datetime import datetime, timezone

from fastapi import HTTPException, status

from dtos.tenant.base import PLANOS_VALIDOS, STATUS_VALIDOS, BrandingDefaultBase


DEFAULT_BRANDING = BrandingDefaultBase().model_dump()


class TenantFactory:

    @staticmethod
    def validate_plano(plano: str) -> None:
        if plano not in PLANOS_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Plano invalido. Validos: {', '.join(PLANOS_VALIDOS)}",
            )

    @staticmethod
    def validate_status(value: str) -> None:
        if value not in STATUS_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status invalido. Validos: {', '.join(STATUS_VALIDOS)}",
            )

    @staticmethod
    def create_tenant_doc(dto, created_by: str | None) -> dict:
        """Monta doc Mongo para insercao.

        Regras:
        - plano validado
        - branding_default: usa default neutro se nao enviado
        - status inicial: 'ativo'
        - auditoria: created_by + timestamp
        """
        TenantFactory.validate_plano(dto.plano)
        branding = dto.branding_default.model_dump() if dto.branding_default else DEFAULT_BRANDING
        now = datetime.now(timezone.utc)
        return {
            "tenant_id": dto.tenant_id,
            "nome": dto.nome,
            "plano": dto.plano,
            "status": "ativo",
            "limites": dto.limites.model_dump(),
            "branding_default": branding,
            "admin_user_id": None,
            "created_at": now,
            "updated_at": None,
            "created_by": created_by,
            "audit_log": [{
                "user_id": created_by,
                "timestamp": now,
                "action": "tenant_created",
                "changes": {"tenant_id": dto.tenant_id, "plano": dto.plano},
            }],
        }

    @staticmethod
    def build_update_fields(dto, existing: dict) -> tuple[dict, dict]:
        """Retorna (fields_to_set, audit_changes).

        Campos None no dto nao sao tocados (partial update).
        audit_changes mapeia campo -> {de, para} pra gravar na auditoria.
        """
        fields: dict = {}
        audit: dict = {}

        if dto.nome is not None and dto.nome != existing.get("nome"):
            fields["nome"] = dto.nome
            audit["nome"] = {"de": existing.get("nome"), "para": dto.nome}

        if dto.plano is not None and dto.plano != existing.get("plano"):
            TenantFactory.validate_plano(dto.plano)
            fields["plano"] = dto.plano
            audit["plano"] = {"de": existing.get("plano"), "para": dto.plano}

        if dto.status is not None and dto.status != existing.get("status"):
            TenantFactory.validate_status(dto.status)
            fields["status"] = dto.status
            audit["status"] = {"de": existing.get("status"), "para": dto.status}

        if dto.limites is not None:
            novo_lim = dto.limites.model_dump()
            if novo_lim != existing.get("limites"):
                fields["limites"] = novo_lim
                audit["limites"] = {"de": existing.get("limites"), "para": novo_lim}

        if fields:
            fields["updated_at"] = datetime.now(timezone.utc)

        return fields, audit

    @staticmethod
    def build_audit_entry(user_id: str | None, action: str, changes: dict) -> dict:
        return {
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc),
            "action": action,
            "changes": changes,
        }
