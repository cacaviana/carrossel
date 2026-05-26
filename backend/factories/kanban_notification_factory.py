from datetime import datetime, timezone


TIPOS_VALIDOS = {"assigned", "mentioned", "column_changed"}


class KanbanNotificationFactory:

    @staticmethod
    def to_doc(tenant_id: str, user_id: str, card_id: str, type_: str, message: str) -> dict:
        if type_ not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo de notificacao invalido: {type_}")
        return {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "card_id": card_id,
            "type": type_,
            "message": message,
            "is_read": False,
            "created_at": datetime.now(timezone.utc),
        }
