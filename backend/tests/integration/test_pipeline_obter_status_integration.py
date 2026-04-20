"""Integracao Pipeline Obter Status.

Caso de uso: GET /api/pipelines/{id}/status

Criterios de aceite da task (ClickUp 86e0y9c6t):
- Retorna etapa atual
- Porcentagem (etapas concluidas / total * 100)
- Logs resumidos por etapa (agente, ordem, status, duracao)
- ETA estimado (media das duracoes concluidas * etapas restantes)
- 404 quando pipeline nao existe
"""

import pytest


@pytest.fixture
def mock_pipeline_db(monkeypatch):
    """Mocka buscar_pipeline no pipeline_service (nao no pipeline_db_service).

    O service faz `from services.pipeline_db_service import buscar_pipeline` no topo,
    entao a referencia resolvida vive no modulo services.pipeline_service.
    """
    import services.pipeline_service as ps

    pipelines_state: dict[str, dict] = {}

    async def fake_buscar(pipeline_id: str):
        return pipelines_state.get(pipeline_id)

    monkeypatch.setattr(ps, "buscar_pipeline", fake_buscar, raising=True)
    return pipelines_state


def _pipeline_mock(pipeline_id="p1", status="aguardando_aprovacao", etapa_atual="art_director", etapas=None):
    return {
        "id": pipeline_id,
        "tema": "teste",
        "formato": "carrossel",
        "modo_funil": False,
        "status": status,
        "etapa_atual": etapa_atual,
        "brand_slug": None,
        "avatar_mode": "livre",
        "created_at": "2026-04-20T10:00:00+00:00",
        "etapas": etapas or [],
    }


class TestObterStatusPipeline:
    """GET /api/pipelines/{id}/status"""

    def test_pipeline_inexistente_retorna_404(self, client, admin_headers, mock_pipeline_db):
        resp = client.get("/api/pipelines/nao-existe/status", headers=admin_headers)
        assert resp.status_code == 404

    def test_pipeline_recem_criado_porcentagem_zero(self, client, admin_headers, mock_pipeline_db):
        etapas = [
            {"agente": "strategist",    "ordem": 1, "status": "pendente", "started_at": None, "finished_at": None},
            {"agente": "copywriter",    "ordem": 2, "status": "pendente", "started_at": None, "finished_at": None},
            {"agente": "art_director",  "ordem": 3, "status": "pendente", "started_at": None, "finished_at": None},
            {"agente": "image_generator","ordem": 4, "status": "pendente", "started_at": None, "finished_at": None},
            {"agente": "brand_gate",    "ordem": 5, "status": "pendente", "started_at": None, "finished_at": None},
            {"agente": "content_critic","ordem": 6, "status": "pendente", "started_at": None, "finished_at": None},
        ]
        mock_pipeline_db["p-novo"] = _pipeline_mock(pipeline_id="p-novo", status="pendente", etapa_atual="strategist", etapas=etapas)

        resp = client.get("/api/pipelines/p-novo/status", headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["pipeline_id"] == "p-novo"
        assert body["status"] == "pendente"
        assert body["etapa_atual"] == "strategist"
        assert body["porcentagem"] == 0.0
        assert body["etapas_concluidas"] == 0
        assert body["total_etapas"] == 6
        assert body["eta_segundos"] is None, "sem duracoes nao ha como estimar"
        assert len(body["logs"]) == 6

    def test_pipeline_meio_caminho_porcentagem_parcial(self, client, admin_headers, mock_pipeline_db):
        # 2 etapas concluidas de 6 → 33.3%
        etapas = [
            {"agente": "strategist",    "ordem": 1, "status": "aprovado",
             "started_at": "2026-04-20T10:00:00+00:00", "finished_at": "2026-04-20T10:00:30+00:00"},  # 30s
            {"agente": "copywriter",    "ordem": 2, "status": "aprovado",
             "started_at": "2026-04-20T10:00:30+00:00", "finished_at": "2026-04-20T10:01:00+00:00"},  # 30s
            {"agente": "art_director",  "ordem": 3, "status": "executando", "started_at": "2026-04-20T10:01:00+00:00", "finished_at": None},
            {"agente": "image_generator","ordem": 4, "status": "pendente", "started_at": None, "finished_at": None},
            {"agente": "brand_gate",    "ordem": 5, "status": "pendente", "started_at": None, "finished_at": None},
            {"agente": "content_critic","ordem": 6, "status": "pendente", "started_at": None, "finished_at": None},
        ]
        mock_pipeline_db["p-meio"] = _pipeline_mock(pipeline_id="p-meio", etapa_atual="art_director", etapas=etapas)

        resp = client.get("/api/pipelines/p-meio/status", headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["etapas_concluidas"] == 2
        assert body["total_etapas"] == 6
        assert body["porcentagem"] == pytest.approx(33.3, abs=0.1)
        assert body["etapa_atual"] == "art_director"

        # ETA: media de 30s * 4 pendentes = 120s
        assert body["eta_segundos"] == 120

    def test_pipeline_concluido_porcentagem_100(self, client, admin_headers, mock_pipeline_db):
        etapas = [
            {"agente": f"agente_{i}", "ordem": i, "status": "aprovado",
             "started_at": "2026-04-20T10:00:00+00:00", "finished_at": "2026-04-20T10:00:10+00:00"}
            for i in range(1, 7)
        ]
        mock_pipeline_db["p-ok"] = _pipeline_mock(pipeline_id="p-ok", status="concluido", etapa_atual=None, etapas=etapas)

        resp = client.get("/api/pipelines/p-ok/status", headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["porcentagem"] == 100.0
        assert body["etapas_concluidas"] == 6
        assert body["eta_segundos"] is None, "nada pendente, ETA nao aplicavel"

    def test_logs_contem_duracao_calculada(self, client, admin_headers, mock_pipeline_db):
        etapas = [
            {"agente": "strategist", "ordem": 1, "status": "aprovado",
             "started_at": "2026-04-20T10:00:00+00:00", "finished_at": "2026-04-20T10:00:45+00:00"},
            {"agente": "copywriter", "ordem": 2, "status": "pendente", "started_at": None, "finished_at": None},
        ]
        mock_pipeline_db["p-log"] = _pipeline_mock(pipeline_id="p-log", etapas=etapas)

        resp = client.get("/api/pipelines/p-log/status", headers=admin_headers)
        assert resp.status_code == 200
        logs = resp.json()["logs"]
        assert len(logs) == 2
        assert logs[0]["agente"] == "strategist"
        assert logs[0]["status"] == "aprovado"
        assert logs[0]["duracao_seg"] == 45.0
        assert logs[1]["duracao_seg"] is None

    def test_sem_auth_bloqueia(self, client, mock_pipeline_db):
        """Endpoint protegido por get_current_user."""
        resp = client.get("/api/pipelines/qualquer/status")
        assert resp.status_code in (401, 403)


class TestContrato:
    def test_rota_esta_registrada_no_openapi(self, client):
        resp = client.get("/openapi.json")
        paths = resp.json()["paths"]
        assert "/api/pipelines/{pipeline_id}/status" in paths
        assert "get" in paths["/api/pipelines/{pipeline_id}/status"]

    def test_response_schema_tem_campos_obrigatorios(self, client):
        resp = client.get("/openapi.json")
        schemas = resp.json()["components"]["schemas"]
        schema = schemas["ObterStatusPipelineResponse"]
        props = schema["properties"].keys()
        required_campos = {
            "pipeline_id", "status", "etapa_atual",
            "porcentagem", "etapas_concluidas", "total_etapas",
            "eta_segundos", "logs",
        }
        assert required_campos.issubset(props), f"Campos faltando: {required_campos - set(props)}"
