from pydantic import BaseModel
from typing import Optional


class EtapaStatusLog(BaseModel):
    agente: str
    ordem: int
    status: str
    duracao_seg: Optional[float] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


class ObterStatusPipelineResponse(BaseModel):
    pipeline_id: str
    status: str
    etapa_atual: Optional[str] = None
    porcentagem: float
    etapas_concluidas: int
    total_etapas: int
    eta_segundos: Optional[int] = None
    logs: list[EtapaStatusLog]
