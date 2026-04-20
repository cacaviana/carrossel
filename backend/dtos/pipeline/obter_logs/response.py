from pydantic import BaseModel
from typing import Optional


class CriticoScore(BaseModel):
    """Breakdown do score do Content Critic (6 dimensoes)."""
    clarity: Optional[float] = None
    impact: Optional[float] = None
    originality: Optional[float] = None
    scroll_stop: Optional[float] = None
    cta_strength: Optional[float] = None
    final_score: Optional[float] = None
    decision: Optional[str] = None


class EtapaLog(BaseModel):
    agente: str
    ordem: int
    status: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    latencia_seg: Optional[float] = None
    erro_mensagem: Optional[str] = None
    # Custos e tokens ficam None hoje — instrumentacao pendente.
    tokens_entrada: Optional[int] = None
    tokens_saida: Optional[int] = None
    custo_usd: Optional[float] = None


class ResumoLogs(BaseModel):
    total_etapas: int
    etapas_concluidas: int
    etapas_com_erro: int
    latencia_total_seg: float
    custo_total_usd: Optional[float] = None
    tokens_total: Optional[int] = None


class ObterLogsPipelineResponse(BaseModel):
    pipeline_id: str
    status: str
    etapa_atual: Optional[str] = None
    etapas: list[EtapaLog]
    resumo: ResumoLogs
    critic_score: Optional[CriticoScore] = None
    custos_instrumentados: bool = False  # flag: quando True, tokens_* e custo_* serao preenchidos
