from datetime import datetime, timezone


class KanbanCommentFactory:

    @staticmethod
    def to_doc(dto, card_id: str, tenant_id: str, user_id: str) -> dict:
        return {
            "tenant_id": tenant_id,
            "card_id": card_id,
            "user_id": user_id,
            "text": dto.text.strip(),
            "parent_comment_id": None,
            "mentions": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
            "deleted_at": None,
        }

    @staticmethod
    def validar_permissao_edicao(comment_doc: dict, user_id: str, user_role: str):
        if comment_doc["user_id"] != user_id:
            raise ValueError("Apenas o autor pode editar o comentario")

    @staticmethod
    def validar_permissao_exclusao(comment_doc: dict, user_id: str, user_role: str):
        if comment_doc["user_id"] != user_id and user_role != "admin":
            raise ValueError("Apenas o autor ou Admin pode deletar o comentario")
