from dtos.kanban_activity.listar_atividades.response import AtividadeResponse


class KanbanActivityMapper:

    @staticmethod
    def to_response(doc: dict, user_name: str = "") -> AtividadeResponse:
        return AtividadeResponse(
            id=str(doc["_id"]),
            card_id=doc["card_id"],
            user_id=doc["user_id"],
            user_name=user_name,
            action=doc["action"],
            metadata=doc.get("metadata", {}),
            created_at=doc["created_at"],
        )

    @staticmethod
    def to_list(docs: list[dict], users_map: dict) -> list[AtividadeResponse]:
        activities = []
        for doc in docs:
            user_info = users_map.get(doc["user_id"], {})
            name = user_info.get("name", "Sistema") if doc["user_id"] != "sistema" else "Sistema"
            activities.append(KanbanActivityMapper.to_response(doc, user_name=name))
        return activities
