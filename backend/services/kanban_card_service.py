from fastapi import HTTPException

from factories.kanban_card_factory import KanbanCardFactory
from factories.kanban_board_factory import KanbanBoardFactory, COLUNA_CANCELADO
from mappers.kanban_card_mapper import KanbanCardMapper
from data.repositories.mongo.kanban_card_repository import KanbanCardRepository
from data.repositories.mongo.kanban_board_repository import KanbanBoardRepository
from data.repositories.mongo.kanban_comment_repository import KanbanCommentRepository
from services.kanban_activity_service import KanbanActivityService
from services.kanban_notification_service import KanbanNotificationService


class KanbanCardService:

    @staticmethod
    def criar(dto, tenant_id: str, created_by: str):
        board = KanbanBoardRepository.garantir_board_padrao(tenant_id)
        board_id = str(board["_id"])
        doc = KanbanCardFactory.to_doc(dto, board_id, tenant_id, created_by)
        saved = KanbanCardRepository.criar(doc)

        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=str(saved["_id"]),
            user_id=created_by,
            action="card_created",
            metadata={"title": saved["title"]},
        )

        for uid in saved.get("assigned_user_ids", []):
            KanbanNotificationService.notificar(
                tenant_id=tenant_id,
                user_id=uid,
                card_id=str(saved["_id"]),
                type_="assigned",
                message=f"Voce foi atribuido ao card '{saved['title']}'",
            )

        return KanbanCardMapper.to_response(saved)

    @staticmethod
    def buscar(card_id: str, tenant_id: str):
        doc = KanbanCardRepository.buscar_por_id(card_id, tenant_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Card nao encontrado")
        count = KanbanCommentRepository.contar_por_card(card_id, tenant_id)
        return KanbanCardMapper.to_response(doc, comment_count=count)

    @staticmethod
    def listar(tenant_id: str, filtros: dict):
        docs = KanbanCardRepository.listar(tenant_id, filtros)
        comment_counts = {}
        for d in docs:
            cid = str(d["_id"])
            comment_counts[cid] = KanbanCommentRepository.contar_por_card(cid, tenant_id)
        return KanbanCardMapper.to_list(docs, comment_counts)

    @staticmethod
    def atualizar(card_id: str, dto, tenant_id: str, user_id: str):
        fields = KanbanCardFactory.to_update_fields(dto)
        if not fields:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        updated = KanbanCardRepository.atualizar(card_id, tenant_id, fields)
        if not updated:
            raise HTTPException(status_code=404, detail="Card nao encontrado")

        for campo, valor in fields.items():
            if campo == "updated_at":
                continue
            KanbanActivityService.registrar(
                tenant_id=tenant_id,
                card_id=card_id,
                user_id=user_id,
                action="field_edited",
                metadata={"field_name": campo, "new_value": str(valor)},
            )

        return KanbanCardMapper.to_response(updated)

    @staticmethod
    def mover_manual(card_id: str, dto, tenant_id: str, user_id: str):
        card = KanbanCardRepository.buscar_por_id(card_id, tenant_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card nao encontrado")
        KanbanBoardFactory.validar_coluna_destino(dto.column_id, card["column_id"])
        from_col = card["column_id"]
        moved = KanbanCardRepository.mover(card_id, tenant_id, dto.column_id)

        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=card_id,
            user_id=user_id,
            action="column_changed",
            metadata={"from_column": from_col, "to_column": dto.column_id},
        )

        for uid in card.get("assigned_user_ids", []):
            KanbanNotificationService.notificar(
                tenant_id=tenant_id,
                user_id=uid,
                card_id=card_id,
                type_="column_changed",
                message=f"Card '{card['title']}' moveu para {dto.column_id}",
            )

        return KanbanCardMapper.to_response(moved)

    @staticmethod
    def mover_pipeline(card_id: str, column_destino: str, tenant_id: str):
        card = KanbanCardRepository.buscar_por_id(card_id, tenant_id)
        if not card:
            return None
        KanbanBoardFactory.validar_movimentacao_pipeline(column_destino)
        from_col = card["column_id"]
        moved = KanbanCardRepository.mover(card_id, tenant_id, column_destino)

        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=card_id,
            user_id="sistema",
            action="column_changed",
            metadata={"from_column": from_col, "to_column": column_destino},
        )

        for uid in card.get("assigned_user_ids", []):
            KanbanNotificationService.notificar(
                tenant_id=tenant_id,
                user_id=uid,
                card_id=card_id,
                type_="column_changed",
                message=f"Card '{card['title']}' moveu automaticamente para {column_destino}",
            )

        return KanbanCardMapper.to_response(moved)

    @staticmethod
    def atribuir_responsaveis(card_id: str, dto, tenant_id: str, user_id: str):
        card = KanbanCardRepository.buscar_por_id(card_id, tenant_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card nao encontrado")
        old_ids = set(card.get("assigned_user_ids", []))
        new_ids = set(dto.user_ids)
        updated = KanbanCardRepository.atribuir_responsaveis(card_id, tenant_id, dto.user_ids)

        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=card_id,
            user_id=user_id,
            action="assignee_changed",
            metadata={"old": list(old_ids), "new": list(new_ids)},
        )

        for uid in new_ids - old_ids:
            KanbanNotificationService.notificar(
                tenant_id=tenant_id,
                user_id=uid,
                card_id=card_id,
                type_="assigned",
                message=f"Voce foi atribuido ao card '{card['title']}'",
            )

        return KanbanCardMapper.to_response(updated)

    @staticmethod
    def vincular_artefato(card_id: str, dto, tenant_id: str, user_id: str):
        fields = KanbanCardFactory.to_artefato_fields(dto)
        if not fields:
            raise HTTPException(status_code=400, detail="Nenhum artefato para vincular")
        updated = KanbanCardRepository.atualizar(card_id, tenant_id, fields)
        if not updated:
            raise HTTPException(status_code=404, detail="Card nao encontrado")

        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=card_id,
            user_id=user_id,
            action="drive_linked" if "drive_link" in fields else "pdf_exported",
            metadata={k: v for k, v in fields.items() if k != "updated_at"},
        )

        return KanbanCardMapper.to_response(updated)
