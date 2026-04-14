"""Mapper do dominio Auth — so conversao, nunca valida."""

from dtos.auth.login.response import LoginResponse
from dtos.auth.criar_usuario.response import UsuarioResponse
from dtos.auth.me.response import MeResponse
from dtos.auth.convidar_usuario.response import ConviteResponse
from dtos.auth.listar_usuarios.response import UsuarioItem, ListarUsuariosResponse


class AuthMapper:
    """Converte documentos MongoDB em DTOs de response."""

    @staticmethod
    def to_login_response(user_doc: dict, token: str) -> LoginResponse:
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user_id=str(user_doc["_id"]),
            tenant_id=user_doc["tenant_id"],
            role=user_doc["role"],
            name=user_doc["name"],
            email=user_doc["email"],
        )

    @staticmethod
    def to_usuario_response(user_doc: dict) -> UsuarioResponse:
        return UsuarioResponse(
            user_id=str(user_doc["_id"]),
            tenant_id=user_doc["tenant_id"],
            email=user_doc["email"],
            name=user_doc["name"],
            role=user_doc["role"],
            avatar_url=user_doc.get("avatar_url"),
            created_at=user_doc["created_at"],
        )

    @staticmethod
    def to_me_response(user_doc: dict) -> MeResponse:
        return MeResponse(
            user_id=str(user_doc["_id"]),
            tenant_id=user_doc["tenant_id"],
            role=user_doc["role"],
            email=user_doc["email"],
            name=user_doc["name"],
            avatar_url=user_doc.get("avatar_url"),
            created_at=user_doc.get("created_at"),
        )

    @staticmethod
    def to_convite_response(invite_doc: dict, base_url: str) -> ConviteResponse:
        return ConviteResponse(
            invite_token=invite_doc["token"],
            email=invite_doc["email"],
            name=invite_doc["name"],
            role=invite_doc["role"],
            expires_at=invite_doc["expires_at"],
            invite_url=f"{base_url}/aceitar-convite?token={invite_doc['token']}",
        )

    @staticmethod
    def to_usuario_item(user_doc: dict) -> UsuarioItem:
        return UsuarioItem(
            user_id=str(user_doc["_id"]),
            email=user_doc["email"],
            name=user_doc["name"],
            role=user_doc["role"],
            avatar_url=user_doc.get("avatar_url"),
            created_at=user_doc["created_at"],
            deleted_at=user_doc.get("deleted_at"),
        )

    @staticmethod
    def to_listar_response(user_docs: list[dict]) -> ListarUsuariosResponse:
        items = [AuthMapper.to_usuario_item(doc) for doc in user_docs]
        return ListarUsuariosResponse(
            usuarios=items,
            total=len(items),
        )
