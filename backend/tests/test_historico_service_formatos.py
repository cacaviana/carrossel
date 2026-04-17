"""Testes unitarios — services/historico_service.py (camada OPACA) pros 3 formatos.

Complementa o test_historico_service.py (que cobre carrossel) estendendo pros
novos formatos: PostUnico, CapaReels, Thumbnail.

Valida que:
 - Service NAO acessa campos do model — so chama metodos publicos do repo
 - Service SEMPRE passa tenant_id nas queries (regra IT Valley)
 - Service usa Mapper pra converter Model -> DTO
 - Service e POLIMORFICO — mesmo codigo atende os 3 formatos

Casos de uso cobertos (parametrizados):
  - Listar (PostsUnicos/CapasReels/Thumbnails)
  - Obter (PostUnico/CapaReels/Thumbnail)
  - Excluir (PostUnico/CapaReels/Thumbnail)
"""

import asyncio
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.historico_service import HistoricoService
from models.historico import HistoricoModel


def _run(coro):
    return asyncio.run(coro)


def _make_model(formato="post_unico", titulo="x"):
    m = HistoricoModel()
    m.id = uuid.uuid4()
    m.tenant_id = "itvalley"
    m.titulo = titulo
    m.formato = formato
    m.status = "completo"
    m.disciplina = "D7"
    m.tecnologia_principal = "RAG"
    m.tipo_carrossel = None
    m.total_slides = 1
    m.final_score = 8.0
    m.legenda_linkedin = f"Legenda {formato}"
    m.google_drive_link = f"https://drive/x-{formato}"
    m.google_drive_folder_name = f"{formato} - 2026-04-17"
    m.pipeline_id = "pipe-X"
    m.created_at = datetime.now(timezone.utc)
    return m


FORMATOS_NOVOS = ["post_unico", "capa_reels", "thumbnail_youtube"]


# =============================================================================
# Listar (PostsUnicos / CapasReels / Thumbnails)
# =============================================================================
class TestListarPorFormato:
    @pytest.mark.parametrize("formato", FORMATOS_NOVOS)
    def test_listar_aplicando_filtro_de_formato(self, formato):
        models = [_make_model(formato=formato, titulo=f"item-{i}") for i in range(3)]
        repo = MagicMock()
        repo.list = AsyncMock(return_value=models)

        service = HistoricoService(repo)
        result = _run(service.listar(tenant_id="itvalley", filters={"formato": formato}))

        assert result["total"] == 3
        assert all(i.formato == formato for i in result["items"])

    @pytest.mark.parametrize("formato", FORMATOS_NOVOS)
    def test_listar_tenant_id_obrigatorio(self, formato):
        repo = MagicMock()
        repo.list = AsyncMock(return_value=[])
        service = HistoricoService(repo)

        _run(service.listar(tenant_id="tenant-A", filters={"formato": formato}))
        args = repo.list.await_args
        # (tenant_id, filters)
        assert args.args[0] == "tenant-A"
        assert args.args[1]["formato"] == formato


# =============================================================================
# Obter (PostUnico / CapaReels / Thumbnail)
# =============================================================================
class TestObterPorFormato:
    @pytest.mark.parametrize("formato", FORMATOS_NOVOS)
    def test_obter_retorna_response_com_formato_correto(self, formato):
        m = _make_model(formato=formato)
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=m)
        service = HistoricoService(repo)

        result = _run(service.buscar(str(m.id), tenant_id="itvalley"))
        assert result is not None
        assert result.formato == formato
        assert result.legenda_linkedin == f"Legenda {formato}"

    @pytest.mark.parametrize("formato", FORMATOS_NOVOS)
    def test_obter_404_quando_nao_encontrado(self, formato):
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=None)
        service = HistoricoService(repo)
        result = _run(service.buscar("fake-id", tenant_id="itvalley"))
        assert result is None

    @pytest.mark.parametrize("formato", FORMATOS_NOVOS)
    def test_obter_nao_retorna_item_de_outro_tenant(self, formato):
        """Repo ja filtra por tenant — simulamos o comportamento retornando None
        quando get_by_id e chamado com tenant errado."""
        m = _make_model(formato=formato)

        async def fake_get(id, tenant_id):
            # Simula filtro por tenant
            if tenant_id != m.tenant_id:
                return None
            return m

        repo = MagicMock()
        repo.get_by_id = AsyncMock(side_effect=fake_get)
        service = HistoricoService(repo)

        result_errado = _run(service.buscar(str(m.id), tenant_id="outro-tenant"))
        result_certo = _run(service.buscar(str(m.id), tenant_id="itvalley"))

        assert result_errado is None
        assert result_certo is not None


# =============================================================================
# Excluir (PostUnico / CapaReels / Thumbnail)
# =============================================================================
class TestExcluirPorFormato:
    @pytest.mark.parametrize("formato", FORMATOS_NOVOS)
    def test_excluir_propaga_tenant_id(self, formato):
        m = _make_model(formato=formato)
        repo = MagicMock()
        repo.soft_delete = AsyncMock(return_value=True)
        service = HistoricoService(repo)

        ok = _run(service.deletar(str(m.id), tenant_id="itvalley"))
        assert ok is True
        args = repo.soft_delete.await_args
        assert args.args[1] == "itvalley"

    @pytest.mark.parametrize("formato", FORMATOS_NOVOS)
    def test_excluir_bloqueia_cross_tenant(self, formato):
        """Simular que o repo filtra por tenant — se id existe mas tenant errado,
        retorna False."""
        async def fake_delete(id, tenant_id):
            return tenant_id == "itvalley"

        repo = MagicMock()
        repo.soft_delete = AsyncMock(side_effect=fake_delete)
        service = HistoricoService(repo)

        assert _run(service.deletar("id-X", tenant_id="itvalley")) is True
        assert _run(service.deletar("id-X", tenant_id="outro")) is False


# =============================================================================
# Camada opaca — service so conhece tipagens BaseRepository
# =============================================================================
class TestServiceOpacidade:
    """Service nunca acessa campos do model. Usa Factory/Mapper."""

    def test_service_nao_referencia_campos_internos(self):
        """Service chama apenas metodos publicos do repo e retorna Items/Response."""
        import inspect
        from services import historico_service
        src = inspect.getsource(historico_service)
        # Nao deve ter 'model.disciplina', 'model.final_score', etc.
        for campo in ("disciplina", "final_score", "legenda_linkedin", "pipeline_id"):
            padrao_proibido = f"model.{campo}"
            assert padrao_proibido not in src, (
                f"Service deve ser opaco — nao pode acessar model.{campo}"
            )
