from pydantic import BaseModel
from typing import Optional, Any


class AprovarEtapaRequest(BaseModel):
    """Aprova uma etapa do pipeline.

    Aceita duas formas de payload (backward-compatible):

    - Forma legada: `saida_editada` (string JSON-stringified).
    - Forma nova do frontend: `dados_editados` (dict estruturado) + `etapa` (nome do agente).

    Quando `dados_editados` estiver presente, ele tem prioridade — o service
    serializa o dict para string JSON antes de persistir.
    """

    saida_editada: Optional[str] = None
    dados_editados: Optional[Any] = None
    etapa: Optional[str] = None
