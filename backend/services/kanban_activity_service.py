from factories.kanban_activity_factory import KanbanActivityFactory
from mappers.kanban_activity_mapper import KanbanActivityMapper
from data.repositories.mongo.kanban_activity_repository import KanbanActivityRepository
from data.repositories.mongo.auth_repository import AuthRepository


class KanbanActivityService:

    @staticmethod
    def registrar(tenant_id: str, card_id: str, user_id: str, action: str, metadata: dict = {}):
        doc = KanbanActivityFactory.to_doc(tenant_id, card_id, user_id, action, metadata)
        KanbanActivityRepository.criar(doc)

    @staticmethod
    def listar(card_id: str, tenant_id: str, limit: int = 50, skip: int = 0):
        docs = KanbanActivityRepository.listar_por_card(card_id, tenant_id, limit, skip)
        user_ids = list({d["user_id"] for d in docs if d["user_id"] != "sistema"})
        users_map = {}
        for uid in user_ids:
            user = AuthRepository.find_by_id(tenant_id, uid)
            if user:
                users_map[uid] = {"name": user["name"], "avatar_url": user.get("avatar_url")}
        return KanbanActivityMapper.to_list(docs, users_map)
