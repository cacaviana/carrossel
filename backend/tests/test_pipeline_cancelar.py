"""Testes unitarios — Cancelar Pipeline

Cobre:
- PipelineService.cancelar() — regras de negocio
  - pipeline inexistente retorna None
  - pipeline ja completo levanta ValueError
  - pipeline ja cancelado levanta ValueError
  - pipeline em andamento atualiza status para 'cancelado'
- POST /api/pipelines/{id}/cancelar — router (camada opaca)
  - 404 se pipeline nao existe
  - 400 se pipeline ja completo/cancelado
  - 200 com status=cancelado em caso de sucesso

Roda async com asyncio.run() (evita dependencia de pytest-asyncio).
"""

import asyncio
import sys, os
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from services.pipeline_service import PipelineService


def _run(coro):
    """Helper para rodar funcoes async em testes sincronos."""
    return asyncio.run(coro)


# ===================================================================
# Service — regras de negocio de cancelamento
# ===================================================================
class TestPipelineServiceCancelar:
    def test_pipeline_inexistente_retorna_none(self):
        with patch("services.pipeline_service.buscar_pipeline", new=AsyncMock(return_value=None)):
            result = _run(PipelineService.cancelar("id-nao-existe"))
        assert result is None

    def test_pipeline_pendente_cancela_com_sucesso(self):
        pipeline_atual = {"id": "p1", "status": "pendente"}
        update_mock = AsyncMock()
        with patch("services.pipeline_service.buscar_pipeline", new=AsyncMock(return_value=pipeline_atual)), \
             patch("services.pipeline_service.atualizar_pipeline", new=update_mock):
            result = _run(PipelineService.cancelar("p1"))

        update_mock.assert_awaited_once_with("p1", {"status": "cancelado"})
        assert result["status"] == "cancelado"
        assert result["pipeline_id"] == "p1"
        assert "mensagem" in result

    def test_pipeline_em_execucao_cancela(self):
        pipeline_atual = {"id": "p2", "status": "executando"}
        with patch("services.pipeline_service.buscar_pipeline", new=AsyncMock(return_value=pipeline_atual)), \
             patch("services.pipeline_service.atualizar_pipeline", new=AsyncMock()):
            result = _run(PipelineService.cancelar("p2"))
        assert result["status"] == "cancelado"

    def test_pipeline_aguardando_aprovacao_cancela(self):
        pipeline_atual = {"id": "p3", "status": "aguardando_aprovacao"}
        with patch("services.pipeline_service.buscar_pipeline", new=AsyncMock(return_value=pipeline_atual)), \
             patch("services.pipeline_service.atualizar_pipeline", new=AsyncMock()):
            result = _run(PipelineService.cancelar("p3"))
        assert result["status"] == "cancelado"

    def test_pipeline_completo_rejeita(self):
        pipeline_atual = {"id": "p4", "status": "completo"}
        with patch("services.pipeline_service.buscar_pipeline", new=AsyncMock(return_value=pipeline_atual)):
            with pytest.raises(ValueError, match="completo"):
                _run(PipelineService.cancelar("p4"))

    def test_pipeline_ja_cancelado_rejeita(self):
        pipeline_atual = {"id": "p5", "status": "cancelado"}
        with patch("services.pipeline_service.buscar_pipeline", new=AsyncMock(return_value=pipeline_atual)):
            with pytest.raises(ValueError, match="cancelado"):
                _run(PipelineService.cancelar("p5"))

    def test_nao_chama_atualizar_quando_ja_cancelado(self):
        """Se pipeline ja esta cancelado, nao deve atualizar no DB."""
        pipeline_atual = {"id": "p6", "status": "cancelado"}
        update_mock = AsyncMock()
        with patch("services.pipeline_service.buscar_pipeline", new=AsyncMock(return_value=pipeline_atual)), \
             patch("services.pipeline_service.atualizar_pipeline", new=update_mock):
            with pytest.raises(ValueError):
                _run(PipelineService.cancelar("p6"))
        update_mock.assert_not_awaited()


# ===================================================================
# Router — camada opaca
# ===================================================================
class TestCancelarPipelineRoute:
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app, raise_server_exceptions=False)

    def test_pipeline_inexistente_retorna_404(self, client):
        with patch("services.pipeline_service.buscar_pipeline", new=AsyncMock(return_value=None)):
            resp = client.post("/api/pipelines/nao-existe/cancelar")
        assert resp.status_code == 404

    def test_pipeline_em_andamento_cancela_200(self, client):
        pipeline_atual = {"id": "pabc", "status": "pendente"}
        with patch("services.pipeline_service.buscar_pipeline", new=AsyncMock(return_value=pipeline_atual)), \
             patch("services.pipeline_service.atualizar_pipeline", new=AsyncMock()):
            resp = client.post("/api/pipelines/pabc/cancelar")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "cancelado"
        assert body["pipeline_id"] == "pabc"

    def test_pipeline_ja_completo_retorna_400(self, client):
        pipeline_atual = {"id": "pxyz", "status": "completo"}
        with patch("services.pipeline_service.buscar_pipeline", new=AsyncMock(return_value=pipeline_atual)):
            resp = client.post("/api/pipelines/pxyz/cancelar")
        assert resp.status_code == 400
        assert "completo" in resp.json()["detail"]

    def test_pipeline_ja_cancelado_retorna_400(self, client):
        pipeline_atual = {"id": "pcan", "status": "cancelado"}
        with patch("services.pipeline_service.buscar_pipeline", new=AsyncMock(return_value=pipeline_atual)):
            resp = client.post("/api/pipelines/pcan/cancelar")
        assert resp.status_code == 400
