from pydantic import BaseModel


class ScoreBase(BaseModel):
    clarity: float
    impact: float
    originality: float
    scroll_stop: float
    cta_strength: float
    final_score: float
    decision: str
    best_variation: str | None = None
