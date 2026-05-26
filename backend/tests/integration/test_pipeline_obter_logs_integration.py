"""Integracao Pipeline Obter Logs.

Caso de uso: GET /api/pipelines/{id}/logs  (ClickUp 86e0y9cby)

Criterios atendidos:
- Logs por etapa com timestamps
- Latencia por etapa (derivada de started/finished)
- Erro por etapa
- Score do Content Critic com breakdown dos 6 criterios

Criterio NAO atendido (custos_instrumentados=False):
- Custo agregado (tokens x preco): chamadas a Claude/Gemini nao gravam tokens
  em pipeline_step hoje. Campos tokens_* e custo_* virao null ate a instrumentacao
  ser implementada (feature futura).
"""

import json as _json
import pytest


@pytest.fixture
def mock_etapas_completas(monkeypatch):
    import services.pipeline_service as ps

    state: dict[str, dict] = {}

    async def fake_buscar(pipeline_id: str, tenant_id: str = "itvalley"):
        return state.get(pipeline_id)

    monkeypatch.setattr(ps, "buscar_etapas_completas", fake_buscar, raising=True)
    return state


def _pipeline_completo(pipeline_id="p1", status="concluido", etapa_atual=None, etapas=None):
    return {
        "id": pipeline_id,
        "tema": "teste",
        "formato": "carrossel",
        "status": status,
        "etapa_atual": etapa_atual,
        "created_at": "2026-04-20T10:00:00+00:00",
        "etapas": etapas or [],
    }


class TestObterLogsPipeline:

    def test_pipeline_inexistente_404(self, client, admin_headers, mock_etapas_completas):
        resp = client.get("/api/pipelines/nao-existe/logs", headers=admin_headers)
        assert resp.status_code == 404

    def test_pipeline_com_etapas_retorna_logs_e_resumo(self, client, admin_headers, mock_etapas_completas):
        etapas = [
            {
                "id": "s1", "agente": "strategist", "ordem": 1, "status": "aprovado",
                "started_at": "2026-04-20T10:00:00+00:00",
                "finished_at": "2026-04-20T10:00:20+00:00",
                "entrada": None, "saida": "{}", "erro_mensagem": None,
                "created_at": "2026-04-20T10:00:00+00:00",
            },
            {
                "id": "s2", "agente": "copywriter", "ordem": 2, "status": "erro",
                "started_at": "2026-04-20T10:00:20+00:00",
                "finished_at": "2026-04-20T10:00:30+00:00",
                "entrada": None, "saida": None, "erro_mensagem": "rate limit",
                "created_at": "2026-04-20T10:00:20+00:00",
            },
        ]
        mock_etapas_completas["p1"] = _pipeline_completo(pipeline_id="p1", status="erro", etapa_atual="copywriter", etapas=etapas)

        resp = client.get("/api/pipelines/p1/logs", headers=admin_headers)
        assert resp.status_code == 200, resp.text
        body = resp.json()

        # Logs por etapa
        assert len(body["etapas"]) == 2
        assert body["etapas"][0]["agente"] == "strategist"
        assert body["etapas"][0]["latencia_seg"] == 20.0
        assert body["etapas"][0]["erro_mensagem"] is None
        assert body["etapas"][1]["status"] == "erro"
        assert body["etapas"][1]["erro_mensagem"] == "rate limit"

        # Resumo
        resumo = body["resumo"]
        assert resumo["total_etapas"] == 2
        assert resumo["etapas_concluidas"] == 1
        assert resumo["etapas_com_erro"] == 1
        assert resumo["latencia_total_seg"] == 20.0

        # Instrumentacao de custo ainda nao disponivel
        assert body["custos_instrumentados"] is False
        assert body["resumo"]["custo_total_usd"] is None
        assert body["resumo"]["tokens_total"] is None
        assert body["etapas"][0]["custo_usd"] is None

    def test_extrai_score_do_content_critic(self, client, admin_headers, mock_etapas_completas):
        critic_saida = _json.dumps({
            "clarity": 9.0,
            "impact": 8.5,
            "originality": 7.0,
            "scroll_stop": 8.0,
            "cta_strength": 9.5,
            "final_score": 8.4,
            "decision": "aprovar",
            "best_variation": 1,
            "feedback": "tudo bem claro",
        })
        etapas = [
            {"id": "s1", "agente": "strategist", "ordem": 1, "status": "aprovado",
             "started_at": "2026-04-20T10:00:00+00:00", "finished_at": "2026-04-20T10:00:10+00:00",
             "entrada": None, "saida": "{}", "erro_mensagem": None, "created_at": None},
            {"id": "s6", "agente": "content_critic", "ordem": 6, "status": "aprovado",
             "started_at": "2026-04-20T10:05:00+00:00", "finished_at": "2026-04-20T10:05:15+00:00",
             "entrada": None, "saida": critic_saida, "erro_mensagem": None, "created_at": None},
        ]
        mock_etapas_completas["p2"] = _pipeline_completo(pipeline_id="p2", etapas=etapas)

        resp = client.get("/api/pipelines/p2/logs", headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()

        assert body["critic_score"] is not None
        cs = body["critic_score"]
        assert cs["clarity"] == 9.0
        assert cs["impact"] == 8.5
        assert cs["originality"] == 7.0
        assert cs["scroll_stop"] == 8.0
        assert cs["cta_strength"] == 9.5
        assert cs["final_score"] == 8.4
        assert cs["decision"] == "aprovar"

    def test_sem_content_critic_concluido_nao_tem_score(self, client, admin_headers, mock_etapas_completas):
        etapas = [
            {"id": "s1", "agente": "strategist", "ordem": 1, "status": "pendente",
             "started_at": None, "finished_at": None,
             "entrada": None, "saida": None, "erro_mensagem": None, "created_at": None},
        ]
        mock_etapas_completas["p3"] = _pipeline_completo(pipeline_id="p3", status="pendente", etapas=etapas)
        resp = client.get("/api/pipelines/p3/logs", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["critic_score"] is None

    def test_saida_critic_invalida_nao_quebra(self, client, admin_headers, mock_etapas_completas):
        """JSON malformado na saida do critic nao pode derrubar o endpoint."""
        etapas = [
            {"id": "s6", "agente": "content_critic", "ordem": 6, "status": "aprovado",
             "started_at": "2026-04-20T10:00:00+00:00", "finished_at": "2026-04-20T10:00:05+00:00",
             "entrada": None, "saida": "nao-e-json-valido {{{", "erro_mensagem": None, "created_at": None},
        ]
        mock_etapas_completas["p4"] = _pipeline_completo(pipeline_id="p4", etapas=etapas)
        resp = client.get("/api/pipelines/p4/logs", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["critic_score"] is None

    def test_sem_auth_bloqueia(self, client):
        resp = client.get("/api/pipelines/qualquer/logs")
        assert resp.status_code in (401, 403)


class TestContrato:
    def test_rota_registrada(self, client):
        paths = client.get("/openapi.json").json()["paths"]
        assert "/api/pipelines/{pipeline_id}/logs" in paths
        assert "get" in paths["/api/pipelines/{pipeline_id}/logs"]

    def test_response_schema_tem_campos_principais(self, client):
        schemas = client.get("/openapi.json").json()["components"]["schemas"]
        s = schemas["ObterLogsPipelineResponse"]
        props = set(s["properties"].keys())
        esperados = {"pipeline_id", "status", "etapa_atual", "etapas", "resumo", "critic_score", "custos_instrumentados"}
        assert esperados.issubset(props), f"Faltando: {esperados - props}"
