"""Testes unitarios — Historico (Carrossel)

Cobre casos de uso:
11. Obter Carrossel (HistoricoService.buscar / GET /historico/{id})
12. Excluir Carrossel (HistoricoService.deletar / DELETE /historico/{id})

Camadas testadas:
- Service (HistoricoService) — delega para Repository e Mapper (camada opaca)
- Mapper (HistoricoMapper) — model -> response
- Factory (HistoricoFactory) — criacao com validacao
- Router (historico.py) — camada opaca que orquestra service + repo
"""

import asyncio
import sys, os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from services.historico_service import HistoricoService
from factories.historico_factory import HistoricoFactory
from mappers.historico_mapper import HistoricoMapper
from models.historico import HistoricoModel


def _run(coro):
    return asyncio.run(coro)


def _make_model(**overrides):
    """Cria um HistoricoModel fake (sem persistir no banco)."""
    defaults = dict(
        id=uuid.uuid4(),
        tenant_id="itvalley",
        titulo="Meu Carrossel",
        formato="carrossel",
        status="completo",
        disciplina="D3",
        tecnologia_principal="XGBoost",
        tipo_carrossel="tutorial",
        total_slides=7,
        final_score=8.5,
        legenda_linkedin="Legenda de teste",
        google_drive_link="https://drive/x",
        google_drive_folder_name="Meu carrossel - 2026-04-17",
        pipeline_id="pipe-1",
        created_at=datetime(2026, 4, 17, tzinfo=timezone.utc),
    )
    defaults.update(overrides)
    m = HistoricoModel()
    for k, v in defaults.items():
        setattr(m, k, v)
    return m


# ===================================================================
# Factory — regras de negocio de criacao
# ===================================================================
class TestHistoricoFactory:
    def test_cria_com_titulo(self):
        model = HistoricoFactory.to_model(titulo="Teste", tenant_id="t1")
        assert model.titulo == "Teste"
        assert model.tenant_id == "t1"
        assert model.formato == "carrossel"  # default
        assert model.status == "completo"    # default

    def test_trim_titulo(self):
        model = HistoricoFactory.to_model(titulo="   Com espacos   ", tenant_id="t1")
        assert model.titulo == "Com espacos"

    def test_rejeita_titulo_vazio(self):
        with pytest.raises(ValueError, match="Titulo"):
            HistoricoFactory.to_model(titulo="", tenant_id="t1")

    def test_rejeita_titulo_so_espacos(self):
        with pytest.raises(ValueError, match="Titulo"):
            HistoricoFactory.to_model(titulo="   ", tenant_id="t1")

    def test_tenant_id_obrigatorio_mantido(self):
        """Factory sempre guarda tenant_id recebido."""
        model = HistoricoFactory.to_model(titulo="x", tenant_id="tenant-A")
        assert model.tenant_id == "tenant-A"

    def test_id_auto_gerado(self):
        m1 = HistoricoFactory.to_model(titulo="a", tenant_id="t")
        m2 = HistoricoFactory.to_model(titulo="b", tenant_id="t")
        assert m1.id != m2.id

    def test_campos_opcionais_null(self):
        model = HistoricoFactory.to_model(titulo="x", tenant_id="t")
        assert model.disciplina is None
        assert model.final_score is None
        assert model.pipeline_id is None


# ===================================================================
# Mapper — Model -> Response
# ===================================================================
class TestHistoricoMapperBuscar:
    def test_mapeia_todos_os_campos(self):
        model = _make_model()
        resp = HistoricoMapper.to_buscar_response(model)
        assert resp.id == model.id
        assert resp.titulo == "Meu Carrossel"
        assert resp.formato == "carrossel"
        assert resp.status == "completo"
        assert resp.disciplina == "D3"
        assert resp.total_slides == 7
        assert resp.final_score == 8.5
        assert resp.legenda_linkedin == "Legenda de teste"
        assert resp.google_drive_link == "https://drive/x"
        assert resp.pipeline_id == "pipe-1"

    def test_mapeia_campos_nulos(self):
        model = _make_model(disciplina=None, final_score=None, legenda_linkedin=None)
        resp = HistoricoMapper.to_buscar_response(model)
        assert resp.disciplina is None
        assert resp.final_score is None
        assert resp.legenda_linkedin is None


class TestHistoricoMapperList:
    def test_lista_vazia(self):
        assert HistoricoMapper.to_list([]) == []

    def test_lista_com_itens(self):
        models = [_make_model(), _make_model(titulo="Outro")]
        items = HistoricoMapper.to_list(models)
        assert len(items) == 2
        assert items[1].titulo == "Outro"

    def test_item_nao_inclui_legenda_linkedin(self):
        """HistoricoItem (list) nao inclui legenda_linkedin — so BuscarResponse."""
        model = _make_model()
        item = HistoricoMapper.to_item(model)
        assert not hasattr(item, "legenda_linkedin")


# ===================================================================
# Service — Obter Carrossel (buscar)
# ===================================================================
class TestHistoricoServiceBuscar:
    def test_buscar_retorna_response_se_encontrado(self):
        model = _make_model()
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=model)

        service = HistoricoService(repo)
        result = _run(service.buscar(str(model.id), tenant_id="itvalley"))

        repo.get_by_id.assert_awaited_once_with(str(model.id), "itvalley")
        assert result is not None
        assert result.id == model.id
        assert result.titulo == "Meu Carrossel"

    def test_buscar_retorna_none_se_nao_encontrado(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=None)

        service = HistoricoService(repo)
        result = _run(service.buscar("id-nao-existe", tenant_id="itvalley"))

        assert result is None

    def test_buscar_passa_tenant_id_ao_repo(self):
        """Regra IT Valley: tenant_id em TODA query."""
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=None)

        service = HistoricoService(repo)
        _run(service.buscar("x", tenant_id="tenant-A"))
        args = repo.get_by_id.await_args
        assert args.args == ("x", "tenant-A")


# ===================================================================
# Service — Excluir Carrossel (deletar)
# ===================================================================
class TestHistoricoServiceDeletar:
    def test_deletar_chama_soft_delete_com_tenant(self):
        repo = MagicMock()
        repo.soft_delete = AsyncMock(return_value=True)

        service = HistoricoService(repo)
        result = _run(service.deletar("id1", tenant_id="itvalley"))

        repo.soft_delete.assert_awaited_once_with("id1", "itvalley")
        assert result is True

    def test_deletar_inexistente_retorna_false(self):
        repo = MagicMock()
        repo.soft_delete = AsyncMock(return_value=False)

        service = HistoricoService(repo)
        result = _run(service.deletar("naoexiste", tenant_id="itvalley"))

        assert result is False

    def test_deletar_passa_tenant_id(self):
        """Multi-tenant: nao pode deletar item de outro tenant."""
        repo = MagicMock()
        repo.soft_delete = AsyncMock(return_value=False)

        service = HistoricoService(repo)
        _run(service.deletar("id1", tenant_id="tenant-B"))
        args = repo.soft_delete.await_args
        assert args.args == ("id1", "tenant-B")


# ===================================================================
# Service — Listar Carrosseis (listar, cobrir transversal ao Obter)
# ===================================================================
class TestHistoricoServiceListar:
    def test_listar_retorna_items_e_total(self):
        models = [_make_model(), _make_model(titulo="Outro")]
        repo = MagicMock()
        repo.list = AsyncMock(return_value=models)

        service = HistoricoService(repo)
        result = _run(service.listar(tenant_id="itvalley"))

        assert result["total"] == 2
        assert len(result["items"]) == 2

    def test_listar_vazio(self):
        repo = MagicMock()
        repo.list = AsyncMock(return_value=[])

        service = HistoricoService(repo)
        result = _run(service.listar(tenant_id="itvalley"))
        assert result["total"] == 0
        assert result["items"] == []

    def test_listar_passa_filters(self):
        repo = MagicMock()
        repo.list = AsyncMock(return_value=[])

        service = HistoricoService(repo)
        _run(service.listar(tenant_id="t1", filters={"formato": "carrossel"}))
        args = repo.list.await_args
        assert args.args[0] == "t1"
        assert args.args[1] == {"formato": "carrossel"}


# ===================================================================
# Router — GET /historico/{id} + DELETE /historico/{id}
# ===================================================================
class TestHistoricoRouter:
    """Com MSSQL_URL vazio, o router cai no path de fallback.
    Aqui testamos o comportamento quando SQL nao esta disponivel.
    """

    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app, raise_server_exceptions=False)

    def test_buscar_sem_sql_configurado_404(self, client):
        """Sem MSSQL, buscar sempre cai no 404 do fallback."""
        with patch("routers.historico._sql_available", return_value=False):
            resp = client.get("/api/historico/qualquer-id")
        assert resp.status_code == 404

    def test_listar_sem_sql_retorna_fallback(self, client):
        """Sem SQL, legado pode retornar lista vazia."""
        with patch("routers.historico._sql_available", return_value=False), \
             patch("routers.historico.listar_historico_legado", new=AsyncMock(return_value=[])):
            resp = client.get("/api/historico")
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert "total" in body

    def test_deletar_sem_sql_sem_legado_500(self, client):
        """Sem SQL e sem legado valido, deletar gera 500."""
        with patch("routers.historico._sql_available", return_value=False), \
             patch("routers.historico.deletar_historico_legado", new=AsyncMock(side_effect=Exception("fail"))):
            resp = client.delete("/api/historico/123")
        assert resp.status_code == 500

    def test_deletar_legado_ok(self, client):
        """Legado bem sucedido: ok=True."""
        with patch("routers.historico._sql_available", return_value=False), \
             patch("routers.historico.deletar_historico_legado", new=AsyncMock(return_value=None)):
            resp = client.delete("/api/historico/456")
        assert resp.status_code == 200
        assert resp.json() == {"ok": True}
