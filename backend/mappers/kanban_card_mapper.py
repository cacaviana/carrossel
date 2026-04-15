from dtos.kanban_card.criar_card.response import CardResponse


class KanbanCardMapper:

    @staticmethod
    def to_response(doc: dict, comment_count: int = 0) -> CardResponse:
        return CardResponse(
            id=str(doc["_id"]),
            board_id=doc["board_id"],
            column_id=doc["column_id"],
            title=doc["title"],
            copy_text=doc.get("copy_text"),
            disciplina=doc.get("disciplina"),
            tecnologia=doc.get("tecnologia"),
            priority=doc["priority"],
            assigned_user_ids=doc.get("assigned_user_ids", []),
            created_by=doc["created_by"],
            pipeline_id=doc.get("pipeline_id"),
            drive_link=doc.get("drive_link"),
            drive_folder_name=doc.get("drive_folder_name"),
            pdf_url=doc.get("pdf_url"),
            image_urls=doc.get("image_urls", []),
            order_in_column=doc.get("order_in_column", 0),
            comment_count=comment_count,
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at"),
            archived_at=doc.get("archived_at"),
        )

    @staticmethod
    def to_list(docs: list[dict], comment_counts: dict = None) -> list[CardResponse]:
        if comment_counts is None:
            comment_counts = {}
        return [
            KanbanCardMapper.to_response(d, comment_count=comment_counts.get(str(d["_id"]), 0))
            for d in docs
        ]
