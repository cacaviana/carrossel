from datetime import datetime, timezone
from factories.kanban_board_factory import COLUNA_COPY


class KanbanCardFactory:

    PRIORIDADES_VALIDAS = {"alta", "media", "baixa"}

    @staticmethod
    def to_doc(dto, board_id: str, tenant_id: str, created_by: str) -> dict:
        KanbanCardFactory._validar_prioridade(dto.priority)
        return {
            "tenant_id": tenant_id,
            "board_id": board_id,
            "column_id": COLUNA_COPY,
            "title": dto.title.strip(),
            "copy_text": getattr(dto, "copy_text", None),
            "disciplina": getattr(dto, "disciplina", None),
            "tecnologia": getattr(dto, "tecnologia", None),
            "priority": dto.priority.lower(),
            "assigned_user_ids": getattr(dto, "assigned_user_ids", []),
            "created_by": created_by,
            "pipeline_id": getattr(dto, "pipeline_id", None),
            "drive_link": None,
            "drive_folder_name": None,
            "pdf_url": None,
            "image_urls": [],
            "order_in_column": 0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
            "archived_at": None,
        }

    @staticmethod
    def to_update_fields(dto) -> dict:
        fields = {}
        for campo in ("title", "copy_text", "disciplina", "tecnologia", "priority"):
            valor = getattr(dto, campo, None)
            if valor is not None:
                if campo == "priority":
                    KanbanCardFactory._validar_prioridade(valor)
                    valor = valor.lower()
                fields[campo] = valor
        if fields:
            fields["updated_at"] = datetime.now(timezone.utc)
        return fields

    @staticmethod
    def to_artefato_fields(dto) -> dict:
        fields = {}
        if dto.drive_link is not None:
            fields["drive_link"] = dto.drive_link
        if dto.drive_folder_name is not None:
            fields["drive_folder_name"] = dto.drive_folder_name
        if dto.pdf_url is not None:
            fields["pdf_url"] = dto.pdf_url
        if dto.image_urls is not None:
            fields["image_urls"] = dto.image_urls
        if fields:
            fields["updated_at"] = datetime.now(timezone.utc)
        return fields

    @staticmethod
    def _validar_prioridade(priority: str):
        if priority.lower() not in KanbanCardFactory.PRIORIDADES_VALIDAS:
            raise ValueError(f"Prioridade invalida: {priority}")
