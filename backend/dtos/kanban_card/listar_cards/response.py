from pydantic import BaseModel
from dtos.kanban_card.criar_card.response import CardResponse


class ListarCardsResponse(BaseModel):
    cards: list[CardResponse]
    total: int
