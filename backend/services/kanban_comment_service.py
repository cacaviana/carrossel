from fastapi import HTTPException

from factories.kanban_comment_factory import KanbanCommentFactory
from mappers.kanban_comment_mapper import KanbanCommentMapper
from data.repositories.mongo.kanban_comment_repository import KanbanCommentRepository
from data.repositories.mongo.auth_repository import AuthRepository
from services.kanban_activity_service import KanbanActivityService


class KanbanCommentService:

    @staticmethod
    def criar(card_id: str, dto, tenant_id: str, user_id: str, user_name: str):
        doc = KanbanCommentFactory.to_doc(dto, card_id, tenant_id, user_id)
        saved = KanbanCommentRepository.criar(doc)

        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=card_id,
            user_id=user_id,
            action="comment_added",
            metadata={"comment_id": str(saved["_id"])},
        )

        return KanbanCommentMapper.to_response(saved, user_name=user_name)

    @staticmethod
    def listar(card_id: str, tenant_id: str):
        docs = KanbanCommentRepository.listar_por_card(card_id, tenant_id)
        user_ids = list({d["user_id"] for d in docs})
        users_map = {}
        for uid in user_ids:
            user = AuthRepository.find_by_id(tenant_id, uid)
            if user:
                users_map[uid] = {"name": user["name"], "avatar_url": user.get("avatar_url")}
        return KanbanCommentMapper.to_list(docs, users_map)

    @staticmethod
    def editar(comment_id: str, dto, tenant_id: str, user_id: str, user_role: str):
        comment = KanbanCommentRepository.buscar_por_id(comment_id, tenant_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comentario nao encontrado")
        try:
            KanbanCommentFactory.validar_permissao_edicao(comment, user_id, user_role)
        except ValueError as e:
            raise HTTPException(status_code=403, detail=str(e))
        updated = KanbanCommentRepository.atualizar(comment_id, tenant_id, dto.text)

        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=comment["card_id"],
            user_id=user_id,
            action="comment_edited",
            metadata={"comment_id": comment_id},
        )

        user = AuthRepository.find_by_id(tenant_id, user_id)
        user_name = user["name"] if user else "Desconhecido"
        return KanbanCommentMapper.to_response(updated, user_name=user_name)

    @staticmethod
    def deletar(comment_id: str, tenant_id: str, user_id: str, user_role: str):
        comment = KanbanCommentRepository.buscar_por_id(comment_id, tenant_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comentario nao encontrado")
        try:
            KanbanCommentFactory.validar_permissao_exclusao(comment, user_id, user_role)
        except ValueError as e:
            raise HTTPException(status_code=403, detail=str(e))
        KanbanCommentRepository.soft_delete(comment_id, tenant_id)

        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=comment["card_id"],
            user_id=user_id,
            action="comment_deleted",
            metadata={"comment_id": comment_id},
        )

        return {"detail": "Comentario deletado"}
