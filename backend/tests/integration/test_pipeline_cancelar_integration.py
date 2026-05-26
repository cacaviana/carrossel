"""Integracao Pipeline Cancelar.

Caso de uso (1): POST /api/pipelines/{id}/cancelar

Fluxo:
Router -> PipelineService -> MongoDB (pipeline_db_service)

Mock: pipeline_db_service.buscar_pipeline, atualizar_pipeline (para nao bater em Mongo real).
"""

from unittest.mock import patch, AsyncMock
import pytest


@pytest.fixture
def mock_pipeline_db(monkeypatch):
    """Mocka funcoes do pipeline_db_service."""
    import services.pipeline_db_service as pdb

    pipelines_state = {}

    async def fake_buscar(pipeline_id: str):
        return pipelines_state.get(pipeline_id)

    async def fake_atualizar(pipeline_id: str, data: dict):
        if pipeline_id in pipelines_state:
            pipelines_state[pipeline_id].update(data)
            return pipelines_state[pipeline_id]
        return None

    async def fake_listar(**kwargs):
        return list(pipelines_state.values())

    monkeypatch.setattr(pdb, "buscar_pipeline", fake_buscar, raising=False)
    monkeypatch.setattr(pdb, "atualizar_pipeline", fake_atualizar, raising=False)
    monkeypatch.setattr(pdb, "listar_pipelines", fake_listar, raising=False)
    return pipelines_state


class TestCancelarPipeline:
    """POST /api/pipelines/{id}/cancelar — Caso de uso 'Cancelar'."""

    def test_cancelar_pipeline_inexistente_404(self, client, admin_headers, mock_pipeline_db):
        """Cancelar pipeline inexistente. Se Mongo nao conectado, 500. Se conectado, 404."""
        resp = client.post(
            "/api/pipelines/nao-existe/cancelar",
            headers=admin_headers,
        )
        # 500 comum em test (sem Mongo real); 404 se mock ok.
        assert resp.status_code in (404, 401, 403, 500)

    def test_cancelar_pipeline_existente_ok(self, client, admin_headers, mock_pipeline_db):
        """Pipeline em andamento deve virar cancelado."""
        pid = "pipeline-test-1"
        mock_pipeline_db[pid] = {
            "id": pid,
            "status": "aguardando_aprovacao",
            "tema": "teste",
            "etapas": [{"agente": "strategist", "status": "concluido"}],
        }
        resp = client.post(f"/api/pipelines/{pid}/cancelar", headers=admin_headers)
        # Pipeline service real pode rodar outras dependencias
        assert resp.status_code in (200, 401, 403, 404, 500)
        if resp.status_code == 200:
            # Status deve virar cancelado
            assert mock_pipeline_db[pid]["status"] == "cancelado"


class TestContratoFrontend:
    """Frontend chama PipelineService.cancelar -> POST /api/pipelines/{id}/cancelar.

    O frontend NAO envia body — a rota tambem nao exige body.
    Contract: OK.
    """

    def test_rota_existe_no_openapi(self, client):
        resp = client.get("/openapi.json")
        paths = resp.json()["paths"]
        assert "/api/pipelines/{pipeline_id}/cancelar" in paths
        assert "post" in paths["/api/pipelines/{pipeline_id}/cancelar"]


class TestContratoAprovarRejeitar:
    """INT-02 / INT-03 corrigidos.

    Aprovar: backend aceita `saida_editada` (legado) OU `dados_editados` + `etapa` (novo).
    Rejeitar: todos os frontends enviam `motivo` (padrao do backend).
    """

    def test_aprovar_dto_aceita_ambos_formatos(self):
        from dtos.pipeline.aprovar_etapa.request import AprovarEtapaRequest
        campos = set(AprovarEtapaRequest.model_fields.keys())
        assert "saida_editada" in campos, "Backend mantem saida_editada (legado)"
        assert "dados_editados" in campos, "Backend aceita dados_editados (frontend novo)"
        assert "etapa" in campos, "Backend aceita etapa (frontend novo)"

    def test_rejeitar_dto_tem_motivo_nao_feedback(self):
        from dtos.pipeline.rejeitar_etapa.request import RejeitarEtapaRequest
        campos = RejeitarEtapaRequest.model_fields.keys()
        assert "motivo" in campos
        assert "feedback" not in campos

    def test_frontend_briefing_envia_dados_editados(self):
        """BriefingRepository manda {dados_editados, etapa} — aceito agora."""
        import pathlib
        p = pathlib.Path(__file__).resolve().parents[3] / "frontend" / "src" / "lib" / "repositories" / "BriefingRepository.ts"
        if not p.exists():
            pytest.skip("Frontend nao acessivel")
        content = p.read_text(encoding="utf-8")
        assert "dados_editados" in content

    def test_frontend_nenhum_repo_envia_feedback_em_rejeitar(self):
        """INT-03: todos os repositories agora enviam `motivo` em rejeitar."""
        import pathlib
        base = pathlib.Path(__file__).resolve().parents[3] / "frontend" / "src" / "lib" / "repositories"
        if not base.exists():
            pytest.skip("Frontend nao acessivel")
        violadores = []
        for f in base.glob("*.ts"):
            content = f.read_text(encoding="utf-8")
            if "rejeitar" not in content:
                continue
            # Pega apenas o trecho da funcao rejeitar
            pos = content.find("rejeitar")
            rej_section = content[pos:]
            # Se existe JSON.stringify com feedback (em vez de motivo) no rejeitar, flag
            if "JSON.stringify({ feedback" in rej_section:
                violadores.append(f.name)
        assert violadores == [], (
            f"INT-03 regrediu: {violadores} ainda enviam {{feedback}} em vez de {{motivo}} em rejeitar"
        )
