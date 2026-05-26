from fastapi import HTTPException

from factories.kanban_notification_factory import KanbanNotificationFactory
from mappers.kanban_notification_mapper import KanbanNotificationMapper
from data.repositories.mongo.kanban_notification_repository import KanbanNotificationRepository


class KanbanNotificationService:

    @staticmethod
    def notificar(tenant_id: str, user_id: str, card_id: str, type_: str, message: str):
        doc = KanbanNotificationFactory.to_doc(tenant_id, user_id, card_id, type_, message)
        KanbanNotificationRepository.criar(doc)

    @staticmethod
    def listar(user_id: str, tenant_id: str, limit: int = 20):
        docs = KanbanNotificationRepository.listar(user_id, tenant_id, limit)
        return KanbanNotificationMapper.to_list(docs)

    @staticmethod
    def contar_nao_lidas(user_id: str, tenant_id: str):
        count = KanbanNotificationRepository.contar_nao_lidas(user_id, tenant_id)
        return KanbanNotificationMapper.to_contador_response(count)

    @staticmethod
    def marcar_como_lida(notification_id: str, tenant_id: str):
        success = KanbanNotificationRepository.marcar_como_lida(notification_id, tenant_id)
        if not success:
            raise HTTPException(status_code=404, detail="Notificacao nao encontrada")
        return {"detail": "Marcada como lida"}

    @staticmethod
    def marcar_todas_lidas(user_id: str, tenant_id: str):
        count = KanbanNotificationRepository.marcar_todas_lidas(user_id, tenant_id)
        return {"detail": f"{count} notificacoes marcadas como lidas"}
