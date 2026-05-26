"""DTOs base do dominio Anuncio (pos-pivot 2026-04-23).

Anuncio = 1 formato 1080x1350 com copy de venda.
- headline (max 40), descricao (max 125), cta (max 30) -- RN-017
- 1 image_url unica (nao mais array de dimensoes)
- status: rascunho|gerando|completo|erro|cancelado

Traducao para o frontend:
- status db: rascunho|gerando|completo|erro|cancelado
- status frontend: rascunho|em_andamento|concluido|erro|cancelado
  (traducao feita no Mapper)
"""
from pydantic import BaseModel, Field


class CopyResponse(BaseModel):
    """Copy de venda (RN-017)."""
    headline: str = Field(default="", max_length=40)
    descricao: str = Field(default="", max_length=125)
    cta: str = Field(default="", max_length=30)


class AnuncioResponse(BaseModel):
    """Resposta completa de um anuncio. Casamento com AnuncioDTO do frontend."""
    # Pydantic BaseModel tem um metodo `.copy()` legado -- silenciamos o warning de shadow
    # porque o contrato com o frontend exige o campo 'copy' aninhado.
    model_config = {"protected_namespaces": (), "populate_by_name": True}

    id: str
    tenant_id: str
    titulo: str
    copy: CopyResponse
    status: str                                  # em_andamento|concluido|erro|cancelado|rascunho
    etapa_funil: str = "avulso"
    pipeline_id: str = ""
    pipeline_funil_id: str = ""
    image_url: str = ""
    brand_gate_score: float | None = None
    brand_gate_feedback: str = ""
    tentativas: int = 0
    drive_folder_link: str = ""
    criado_por: str = ""
    created_at: str = ""
    updated_at: str = ""
    deleted_at: str = ""
