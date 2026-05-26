"""Mapper do dominio Anuncio (pos-pivot 2026-04-23). So converte, nunca valida."""
from datetime import datetime
from typing import Optional

from dtos.anuncio.base import AnuncioResponse, CopyResponse
from dtos.anuncio.criar_anuncio.response import CriarAnuncioResponse
from dtos.anuncio.obter_anuncio.response import ObterAnuncioResponse
from dtos.anuncio.editar_anuncio.response import EditarAnuncioResponse
from dtos.anuncio.excluir_anuncio.response import ExcluirAnuncioResponse
from models.anuncio import AnuncioModel


# ---- Mapeamento entre status interno (banco) e o que o frontend espera ----
# Banco: rascunho|gerando|completo|erro|cancelado
# Front: rascunho|em_andamento|concluido|erro|cancelado
_STATUS_DB_TO_FRONT = {
    "rascunho": "rascunho",
    "gerando": "em_andamento",
    "completo": "concluido",
    "erro": "erro",
    "cancelado": "cancelado",
}


def _iso(dt: Optional[datetime]) -> str:
    if dt is None:
        return ""
    try:
        return dt.isoformat().replace("+00:00", "Z") if dt else ""
    except Exception:
        return ""


def _status_front(status_db: Optional[str]) -> str:
    if not status_db:
        return "rascunho"
    return _STATUS_DB_TO_FRONT.get(status_db, status_db)


class AnuncioMapper:

    # --------- ANUNCIO ----------
    @staticmethod
    def to_response(anuncio: AnuncioModel) -> AnuncioResponse:
        return AnuncioResponse(
            id=str(anuncio.id),
            tenant_id=anuncio.tenant_id or "",
            titulo=anuncio.titulo or "",
            copy=CopyResponse(
                headline=anuncio.headline or "",
                descricao=anuncio.descricao or "",
                cta=anuncio.cta or "",
            ),
            status=_status_front(anuncio.status),
            etapa_funil=anuncio.etapa_funil or "avulso",
            pipeline_id=str(anuncio.pipeline_id) if anuncio.pipeline_id else "",
            pipeline_funil_id=str(anuncio.pipeline_funil_id) if anuncio.pipeline_funil_id else "",
            image_url=anuncio.image_url or "",
            brand_gate_score=(
                float(anuncio.brand_gate_score)
                if anuncio.brand_gate_score is not None
                else None
            ),
            brand_gate_feedback=anuncio.brand_gate_feedback or "",
            tentativas=int(anuncio.tentativas or 0),
            drive_folder_link=anuncio.drive_folder_link or "",
            criado_por=anuncio.criado_por or "",
            created_at=_iso(anuncio.created_at),
            updated_at=_iso(anuncio.updated_at),
            deleted_at=_iso(anuncio.deleted_at),
        )

    @staticmethod
    def to_obter_response(anuncio: AnuncioModel) -> ObterAnuncioResponse:
        base = AnuncioMapper.to_response(anuncio)
        return ObterAnuncioResponse(**base.model_dump())

    @staticmethod
    def to_editar_response(anuncio: AnuncioModel) -> EditarAnuncioResponse:
        base = AnuncioMapper.to_response(anuncio)
        return EditarAnuncioResponse(**base.model_dump())

    @staticmethod
    def to_criar_response(anuncio: AnuncioModel) -> CriarAnuncioResponse:
        return CriarAnuncioResponse(
            anuncio_id=str(anuncio.id),
            pipeline_id=str(anuncio.pipeline_id) if anuncio.pipeline_id else "",
            status=_status_front(anuncio.status),
        )

    @staticmethod
    def to_excluir_response(anuncio: AnuncioModel) -> ExcluirAnuncioResponse:
        return ExcluirAnuncioResponse(
            id=str(anuncio.id),
            deleted_at=_iso(anuncio.deleted_at),
            success=True,
        )
