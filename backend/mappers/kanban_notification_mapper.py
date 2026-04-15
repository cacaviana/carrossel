from dtos.kanban_notification.listar_notificacoes.response import NotificacaoResponse
from dtos.kanban_notification.contar_nao_lidas.response import ContadorNaoLidasResponse


class KanbanNotificationMapper:

    @staticmethod
    def to_response(doc: dict) -> NotificacaoResponse:
        return NotificacaoResponse(
            id=str(doc["_id"]),
            card_id=doc["card_id"],
            type=doc["type"],
            message=doc["message"],
            is_read=doc["is_read"],
            created_at=doc["created_at"],
        )

    @staticmethod
    def to_list(docs: list[dict]) -> list[NotificacaoResponse]:
        return [KanbanNotificationMapper.to_response(d) for d in docs]

    @staticmethod
    def to_contador_response(count: int) -> ContadorNaoLidasResponse:
        return ContadorNaoLidasResponse(count=count)
