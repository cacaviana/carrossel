from pydantic import BaseModel
from uuid import UUID
from typing import Optional

from dtos.score.base import ScoreBase


class BuscarScoreResponse(ScoreBase):
    id: UUID
    conteudo_id: UUID
    feedback: Optional[str] = None
