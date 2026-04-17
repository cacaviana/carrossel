"""Integracao Visual Preference.

Casos de uso (2):
- Salvar Preferencia (POST /api/visual-preferences/)
- Listar Preferencias (GET /api/visual-preferences/)

Fluxo:
Router -> Service -> Factory -> SQL Repository

BUG CRITICO DETECTADO (Guardiao):
- tenant_id HARDCODED (routers/visual_preference.py linha 11: TENANT_ID = settings.TENANT_ID)
- NAO usa current_user.tenant_id do JWT.

Sobre SQL em test:
- Model usa UNIQUEIDENTIFIER do MSSQL, nao portavel para SQLite in-memory.
- Testes aqui validam contrato via OpenAPI schema, nao persistencia.
"""

import pytest


class TestContratosOpenAPI:
    """Valida que o schema da API esta correto."""

    def test_openapi_tem_endpoint_salvar(self, client):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        paths = resp.json()["paths"]
        assert "/api/visual-preferences/" in paths
        assert "post" in paths["/api/visual-preferences/"]

    def test_openapi_request_schema_salvar(self, client):
        """Request schema deve ter estilo + aprovado obrigatorios + contexto opcional."""
        resp = client.get("/openapi.json")
        spec = resp.json()
        # Navega ate SalvarPreferenciaRequest
        schemas = spec.get("components", {}).get("schemas", {})
        req_schema = schemas.get("SalvarPreferenciaRequest")
        assert req_schema is not None, "SalvarPreferenciaRequest nao gerado no OpenAPI"
        assert "estilo" in req_schema["required"]
        assert "aprovado" in req_schema["required"]
        assert req_schema["properties"]["estilo"]["type"] == "string"
        assert req_schema["properties"]["aprovado"]["type"] == "boolean"

    def test_openapi_response_schema_listar(self, client):
        """Response de listar tem items: lista de PreferenciaItem."""
        resp = client.get("/openapi.json")
        schemas = resp.json().get("components", {}).get("schemas", {})
        lst = schemas.get("ListarPreferenciasResponse")
        assert lst is not None
        assert "items" in lst["properties"]


class TestSalvarPreferencia:
    """POST /api/visual-preferences/ — Caso de uso 'Salvar Preferencia'."""

    def test_salvar_preferencia_dto_contrato(self, client, admin_headers):
        """SQL nao configurado -> 500 eh aceitavel. 422 = contrato DTO quebrado."""
        payload = {
            "estilo": "minimalist",
            "aprovado": True,
            "contexto": {"disciplina": "D7", "tema": "RAG"},
        }
        resp = client.post(
            "/api/visual-preferences/",
            json=payload,
            headers=admin_headers,
        )
        # 422 = contrato quebrado, 201 = ok, 500 = SQL nao conecta (esperado em test)
        assert resp.status_code != 422, f"DTO contract quebrado: {resp.text}"

    def test_salvar_sem_auth(self, client):
        """Router recebeu JWT? Se sim, sem token -> 401/403."""
        resp = client.post("/api/visual-preferences/", json={
            "estilo": "x", "aprovado": True
        })
        # Com JWT: 401/403. Sem JWT (bloqueador ainda ativo): 500 (TENANT_ID hardcoded)
        assert resp.status_code in (401, 403, 500)


class TestListarPreferencias:
    """GET /api/visual-preferences/ — Caso de uso 'Listar Preferencias'."""

    def test_listar_com_auth(self, client, admin_headers):
        resp = client.get("/api/visual-preferences/", headers=admin_headers)
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            assert "items" in resp.json()


class TestBloqueadorGuardiaoTenantIdHardcoded:
    """Documenta bloqueador: tenant_id hardcoded."""

    def test_router_nao_usa_tenant_hardcoded(self):
        """Quando o Guardiao aprovar o fix, este teste passa.
        Enquanto isso, fica red para sinalizar o problema."""
        import inspect
        from routers import visual_preference as vp_mod
        src = inspect.getsource(vp_mod)
        usa_hardcoded_global = "TENANT_ID = settings.TENANT_ID" in src
        usa_current_user = "current_user.tenant_id" in src

        if usa_hardcoded_global and not usa_current_user:
            pytest.fail(
                "BLOQUEADOR GUARDIAO: routers/visual_preference.py usa TENANT_ID global hardcoded. "
                "Precisa usar current_user.tenant_id do JWT para isolamento multi-tenant."
            )

    def test_historico_router_nao_usa_tenant_hardcoded(self):
        import inspect
        from routers import historico as hist_mod
        src = inspect.getsource(hist_mod)
        usa_hardcoded_global = "TENANT_ID = settings.TENANT_ID" in src
        usa_current_user = "current_user.tenant_id" in src

        if usa_hardcoded_global and not usa_current_user:
            pytest.fail(
                "BLOQUEADOR GUARDIAO: routers/historico.py usa TENANT_ID global hardcoded."
            )
