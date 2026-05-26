"""Testes unitarios — router /api/pipelines/{id}/regerar-imagens.

Cobre o caso de uso "Regerar" pros 3 formatos (PostUnico, Reels, Thumbnail).
Regra: reseta art_director + image_generator + brand_gate + content_critic
       mantendo strategist + copywriter aprovados.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from main import app
    return TestClient(app, raise_server_exceptions=False)


def _pipeline_fake(formato="post_unico"):
    return {
        "id": "pipe-1",
        "formato": formato,
        "etapas": [
            {"id": "s1", "agente": "strategist", "status": "aprovado", "saida": "{}"},
            {"id": "s2", "agente": "copywriter", "status": "aprovado", "saida": "{}"},
            {"id": "s3", "agente": "art_director", "status": "completo", "saida": "{}"},
            {"id": "s4", "agente": "image_generator", "status": "completo", "saida": "{}"},
            {"id": "s5", "agente": "brand_gate", "status": "completo", "saida": "{}"},
            {"id": "s6", "agente": "content_critic", "status": "completo", "saida": "{}"},
        ],
    }


class TestRegerarImagensPipeline:
    @pytest.mark.parametrize("formato", ["post_unico", "capa_reels", "thumbnail_youtube"])
    def test_regerar_sucesso_retorna_etapas_resetadas(self, client, formato):
        pipe = _pipeline_fake(formato=formato)
        with patch("services.pipeline_db_service.buscar_pipeline", new=AsyncMock(return_value=pipe)), \
             patch("services.pipeline_db_service.atualizar_etapa", new=AsyncMock(return_value=None)) as upd_etapa, \
             patch("services.pipeline_db_service.atualizar_pipeline", new=AsyncMock(return_value=None)):
            resp = client.post(f"/api/pipelines/pipe-1/regerar-imagens")

        assert resp.status_code == 200
        body = resp.json()
        assert body["pipeline_id"] == "pipe-1"
        assert set(body["resetadas"]) == {
            "art_director", "image_generator", "brand_gate", "content_critic"
        }

    def test_regerar_404_se_pipeline_nao_existe(self, client):
        with patch("services.pipeline_db_service.buscar_pipeline", new=AsyncMock(return_value=None)):
            resp = client.post("/api/pipelines/fake/regerar-imagens")
        assert resp.status_code == 404

    def test_regerar_preserva_strategist_e_copywriter(self, client):
        pipe = _pipeline_fake()
        atualizacoes: list[tuple] = []

        async def spy_atualizar_etapa(step_id, updates):
            atualizacoes.append((step_id, updates))

        with patch("services.pipeline_db_service.buscar_pipeline", new=AsyncMock(return_value=pipe)), \
             patch("services.pipeline_db_service.atualizar_etapa", new=spy_atualizar_etapa), \
             patch("services.pipeline_db_service.atualizar_pipeline", new=AsyncMock(return_value=None)):
            resp = client.post("/api/pipelines/pipe-1/regerar-imagens")

        assert resp.status_code == 200
        # Strategist (s1) e copywriter (s2) NAO devem ter sido atualizados
        etapas_atualizadas = [step_id for step_id, _ in atualizacoes]
        assert "s1" not in etapas_atualizadas
        assert "s2" not in etapas_atualizadas
        # Demais 4 devem estar
        assert set(etapas_atualizadas) == {"s3", "s4", "s5", "s6"}
        # Status resetado pra pendente
        for _, updates in atualizacoes:
            assert updates["status"] == "pendente"
            assert updates["saida"] is None
            assert updates["entrada"] is None
