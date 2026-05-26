from datetime import datetime, timezone


ACOES_VALIDAS = {
    "card_created",
    "column_changed",
    "assignee_changed",
    "field_edited",
    "comment_added",
    "comment_edited",
    "comment_deleted",
    "image_generated",
    "drive_linked",
    "pdf_exported",
}


class KanbanActivityFactory:

    @staticmethod
    def to_doc(tenant_id: str, card_id: str, user_id: str, action: str, metadata: dict = {}) -> dict:
        if action not in ACOES_VALIDAS:
            raise ValueError(f"Acao invalida: {action}")
        return {
            "tenant_id": tenant_id,
            "card_id": card_id,
            "user_id": user_id,
            "action": action,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc),
        }
