from fastapi import APIRouter, HTTPException, Depends

from dtos.visual_preference.salvar_preferencia.request import SalvarPreferenciaRequest
from dtos.visual_preference.salvar_preferencia.response import SalvarPreferenciaResponse
from dtos.visual_preference.listar_preferencias.response import ListarPreferenciasResponse
from services.visual_preference_service import VisualPreferenceService
from data.connections.database import get_sql_session
from data.repositories.sql.visual_preference_repository import VisualPreferenceRepository

from config import settings
TENANT_ID = settings.TENANT_ID

router = APIRouter(prefix="/visual-preferences", tags=["Visual Preferences"])


def _get_service(session=Depends(get_sql_session)):
    repo = VisualPreferenceRepository(session)
    return VisualPreferenceService(repo)


@router.post("/", response_model=SalvarPreferenciaResponse, status_code=201)
async def salvar_preferencia(
    dto: SalvarPreferenciaRequest,
    service: VisualPreferenceService = Depends(_get_service),
):
    try:
        return await service.salvar(dto, tenant_id=TENANT_ID)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=ListarPreferenciasResponse)
async def listar_preferencias(
    service: VisualPreferenceService = Depends(_get_service),
):
    return await service.listar(tenant_id=TENANT_ID)
