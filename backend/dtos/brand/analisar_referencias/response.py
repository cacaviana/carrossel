from pydantic import BaseModel
from typing import Optional


class CoresExtraidas(BaseModel):
    fundo: str
    gradiente_de: str
    gradiente_ate: str
    card: str
    card_borda: str
    acento_principal: str
    acento_secundario: str
    acento_terciario: Optional[str] = None
    acento_negativo: str = "#F87171"
    texto_principal: str = "#FFFFFF"
    texto_secundario: str


class VisualExtraido(BaseModel):
    estilo_fundo: str
    estilo_elemento: dict
    estilo_card: str
    estilo_texto: str
    estilo_desenho: str
    regras_extras: str


class AnalisarReferenciasResponse(BaseModel):
    cores: CoresExtraidas
    visual: VisualExtraido
    atmosfera: str  # descricao geral da atmosfera detectada
    sugestao_nome: str  # sugestao de nome da marca se nao fornecido
