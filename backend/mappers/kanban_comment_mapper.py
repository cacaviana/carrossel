from dtos.kanban_comment.criar_comentario.response import ComentarioResponse


class KanbanCommentMapper:

    @staticmethod
    def to_response(doc: dict, user_name: str = "", user_avatar_url: str = None) -> ComentarioResponse:
        return ComentarioResponse(
            id=str(doc["_id"]),
            card_id=doc["card_id"],
            user_id=doc["user_id"],
            user_name=user_name,
            user_avatar_url=user_avatar_url,
            text=doc["text"],
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at"),
        )

    @staticmethod
    def to_list(docs: list[dict], users_map: dict) -> list[ComentarioResponse]:
        comments = []
        for doc in docs:
            user_info = users_map.get(doc["user_id"], {})
            comments.append(KanbanCommentMapper.to_response(
                doc,
                user_name=user_info.get("name", "Desconhecido"),
                user_avatar_url=user_info.get("avatar_url"),
            ))
        return comments
