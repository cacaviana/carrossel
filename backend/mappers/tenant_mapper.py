"""Mapper do dominio Tenant — converte doc Mongo para os response DTOs."""


def _iso(dt):
    return dt.isoformat() if dt else None


class TenantMapper:

    @staticmethod
    def to_criar_response(doc: dict, admin_user_id: str, admin_email: str) -> dict:
        return {
            "tenant_id": doc["tenant_id"],
            "nome": doc["nome"],
            "plano": doc["plano"],
            "status": doc["status"],
            "limites": doc["limites"],
            "branding_default": doc["branding_default"],
            "admin_user_id": admin_user_id,
            "admin_email": admin_email,
            "created_at": _iso(doc.get("created_at")),
            "created_by": doc.get("created_by"),
        }

    @staticmethod
    def to_obter_atual_response(doc: dict) -> dict:
        return {
            "tenant_id": doc["tenant_id"],
            "nome": doc["nome"],
            "plano": doc["plano"],
            "status": doc["status"],
            "limites": doc["limites"],
            "branding_default": doc.get("branding_default"),
        }

    @staticmethod
    def to_list_item(doc: dict) -> dict:
        return {
            "tenant_id": doc["tenant_id"],
            "nome": doc["nome"],
            "plano": doc["plano"],
            "status": doc["status"],
            "limites": doc["limites"],
            "created_at": _iso(doc.get("created_at")),
        }

    @staticmethod
    def to_listar_response(docs: list[dict], total: int, limit: int, offset: int) -> dict:
        return {
            "items": [TenantMapper.to_list_item(d) for d in docs],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    @staticmethod
    def to_atualizar_response(doc: dict, updated_by: str | None) -> dict:
        return {
            "tenant_id": doc["tenant_id"],
            "nome": doc["nome"],
            "plano": doc["plano"],
            "status": doc["status"],
            "limites": doc["limites"],
            "branding_default": doc.get("branding_default"),
            "updated_at": _iso(doc.get("updated_at")),
            "updated_by": updated_by,
        }
