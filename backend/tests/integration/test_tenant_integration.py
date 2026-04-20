"""Integracao Tenant — CRUD completo.

Casos de uso:
- POST   /api/tenants            (super_admin)
- GET    /api/tenants/me         (qualquer autenticado)
- GET    /api/tenants            (super_admin)
- PATCH  /api/tenants/{id}       (super_admin ou admin do proprio tenant)
"""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient


def _make_token(**overrides):
    from middleware.auth import create_access_token
    payload = {
        "user_id": "000000000000000000000001",
        "tenant_id": "tenant-A",
        "role": "admin",
        "email": "admin@a.com",
        "name": "Admin A",
    }
    payload.update(overrides)
    return create_access_token(payload)


@pytest.fixture
def super_admin_token():
    return _make_token(role="super_admin", user_id="000000000000000000000099", email="sa@plataforma.com")


@pytest.fixture
def super_admin_headers(super_admin_token):
    return {"Authorization": f"Bearer {super_admin_token}"}


@pytest.fixture
def admin_a_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def admin_b_headers():
    t = _make_token(tenant_id="tenant-B", email="admin@b.com")
    return {"Authorization": f"Bearer {t}"}


@pytest.fixture
def viewer_a_headers():
    t = _make_token(role="viewer", email="v@a.com")
    return {"Authorization": f"Bearer {t}"}


VALID_CRIAR_BODY = {
    "tenant_id": "nova-empresa",
    "nome": "Nova Empresa Ltda",
    "plano": "pro",
    "limites": {"creditos_mes": 500, "marcas_max": 5},
    "admin": {
        "nome": "Ana Admin",
        "email": "ana@novaempresa.com",
        "senha": "Senha123!",
    },
}


def _seed_tenant_a(mock_mongo):
    """Insere tenant-A pra testes de obter_atual e atualizar."""
    mock_mongo.tenants.insert_one({
        "tenant_id": "tenant-A",
        "nome": "Tenant A",
        "plano": "free",
        "status": "ativo",
        "limites": {"creditos_mes": 100, "marcas_max": 1},
        "branding_default": {"paleta_fundo": "#0A0A0A", "paleta_texto": "#FAFAFA",
                              "paleta_destaque": "#A78BFA", "fonte": "Outfit"},
        "admin_user_id": None,
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "updated_at": None,
        "created_by": "seed",
        "audit_log": [],
    })


class TestCriarTenant:

    def test_super_admin_cria_tenant(self, client, super_admin_headers, mock_mongo):
        resp = client.post("/api/tenants", headers=super_admin_headers, json=VALID_CRIAR_BODY)
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["tenant_id"] == "nova-empresa"
        assert body["plano"] == "pro"
        assert body["status"] == "ativo"
        assert body["limites"]["creditos_mes"] == 500
        assert body["branding_default"]["fonte"] == "Outfit"
        assert body["admin_email"] == "ana@novaempresa.com"
        assert len(body["admin_user_id"]) > 10

        # Tenant persistido
        assert mock_mongo.tenants.count_documents({"tenant_id": "nova-empresa"}) == 1
        # Admin user persistido no proprio tenant
        assert mock_mongo.kanban_users.count_documents({
            "tenant_id": "nova-empresa",
            "email": "ana@novaempresa.com",
            "role": "admin",
        }) == 1

    def test_admin_comum_nao_pode_criar(self, client, admin_a_headers, mock_mongo):
        resp = client.post("/api/tenants", headers=admin_a_headers, json=VALID_CRIAR_BODY)
        assert resp.status_code == 403

    def test_viewer_nao_pode_criar(self, client, viewer_a_headers, mock_mongo):
        resp = client.post("/api/tenants", headers=viewer_a_headers, json=VALID_CRIAR_BODY)
        assert resp.status_code == 403

    def test_tenant_id_duplicado_retorna_409(self, client, super_admin_headers, mock_mongo):
        _seed_tenant_a(mock_mongo)
        # Seed insere "tenant-A" (como vem do JWT existente); aqui testamos colisao
        # atraves de outro slug valido previamente inserido.
        mock_mongo.tenants.insert_one({
            "tenant_id": "ja-existe", "nome": "Existente", "plano": "free", "status": "ativo",
            "limites": {"creditos_mes": 10, "marcas_max": 1}, "branding_default": {},
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc), "audit_log": [],
        })
        body = {**VALID_CRIAR_BODY, "tenant_id": "ja-existe"}
        resp = client.post("/api/tenants", headers=super_admin_headers, json=body)
        assert resp.status_code == 409

    def test_tenant_id_invalido_slug(self, client, super_admin_headers, mock_mongo):
        for invalido in ("Tenant-A", "_empresa", "-ab", "ab"):
            body = {**VALID_CRIAR_BODY, "tenant_id": invalido}
            resp = client.post("/api/tenants", headers=super_admin_headers, json=body)
            assert resp.status_code == 422, f"tenant_id {invalido} devia falhar"

    def test_plano_invalido_rejeita(self, client, super_admin_headers, mock_mongo):
        body = {**VALID_CRIAR_BODY, "plano": "premium_super"}
        resp = client.post("/api/tenants", headers=super_admin_headers, json=body)
        # Factory valida o plano na criacao do doc
        assert resp.status_code == 400

    def test_branding_default_aplicado_quando_ausente(self, client, super_admin_headers, mock_mongo):
        """Se o request nao envia branding_default, aplica paleta/fonte padrao."""
        body = {k: v for k, v in VALID_CRIAR_BODY.items()}
        assert "branding_default" not in body
        resp = client.post("/api/tenants", headers=super_admin_headers, json=body)
        assert resp.status_code == 201
        branding = resp.json()["branding_default"]
        assert branding["fonte"] == "Outfit"
        assert branding["paleta_fundo"].startswith("#")

    def test_auditoria_registrada_na_criacao(self, client, super_admin_headers, mock_mongo):
        client.post("/api/tenants", headers=super_admin_headers, json=VALID_CRIAR_BODY)
        doc = mock_mongo.tenants.find_one({"tenant_id": "nova-empresa"})
        assert doc["audit_log"]
        assert doc["audit_log"][0]["action"] == "tenant_created"
        assert doc["audit_log"][0]["user_id"] == "000000000000000000000099"


class TestObterTenantAtual:

    def test_retorna_tenant_do_jwt(self, client, admin_a_headers, mock_mongo):
        _seed_tenant_a(mock_mongo)
        resp = client.get("/api/tenants/me", headers=admin_a_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["tenant_id"] == "tenant-A"
        assert body["plano"] == "free"
        assert body["limites"]["creditos_mes"] == 100

    def test_tenant_nao_existe_retorna_404(self, client, admin_b_headers, mock_mongo):
        """Usuario com JWT de tenant-B mas tenants/tenant-B nao existe no banco."""
        resp = client.get("/api/tenants/me", headers=admin_b_headers)
        assert resp.status_code == 404

    def test_sem_auth_bloqueia(self, client):
        resp = client.get("/api/tenants/me")
        assert resp.status_code in (401, 403)


class TestListarTenants:

    def test_super_admin_lista(self, client, super_admin_headers, mock_mongo):
        _seed_tenant_a(mock_mongo)
        mock_mongo.tenants.insert_one({
            "tenant_id": "tenant-B", "nome": "B", "plano": "pro", "status": "inativo",
            "limites": {"creditos_mes": 200, "marcas_max": 2}, "branding_default": {},
            "created_at": datetime(2026, 2, 1, tzinfo=timezone.utc), "audit_log": [],
        })
        resp = client.get("/api/tenants", headers=super_admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 2
        assert body["limit"] == 20
        assert body["offset"] == 0
        assert len(body["items"]) == 2

    def test_admin_comum_nao_lista(self, client, admin_a_headers, mock_mongo):
        resp = client.get("/api/tenants", headers=admin_a_headers)
        assert resp.status_code == 403

    def test_filtro_status_ativo(self, client, super_admin_headers, mock_mongo):
        _seed_tenant_a(mock_mongo)
        mock_mongo.tenants.insert_one({
            "tenant_id": "tenant-B", "nome": "B", "plano": "pro", "status": "inativo",
            "limites": {"creditos_mes": 200, "marcas_max": 2}, "branding_default": {},
            "created_at": datetime(2026, 2, 1, tzinfo=timezone.utc), "audit_log": [],
        })
        resp = client.get("/api/tenants?status=ativo", headers=super_admin_headers)
        body = resp.json()
        assert body["total"] == 1
        assert body["items"][0]["tenant_id"] == "tenant-A"

    def test_filtro_status_invalido_retorna_400(self, client, super_admin_headers, mock_mongo):
        resp = client.get("/api/tenants?status=pausado", headers=super_admin_headers)
        assert resp.status_code == 400

    def test_paginacao(self, client, super_admin_headers, mock_mongo):
        for i in range(5):
            mock_mongo.tenants.insert_one({
                "tenant_id": f"t{i}", "nome": f"T{i}", "plano": "free", "status": "ativo",
                "limites": {"creditos_mes": 10, "marcas_max": 1}, "branding_default": {},
                "created_at": datetime(2026, 1, i + 1, tzinfo=timezone.utc), "audit_log": [],
            })
        resp = client.get("/api/tenants?limit=2&offset=2", headers=super_admin_headers)
        body = resp.json()
        assert body["total"] == 5
        assert body["limit"] == 2
        assert body["offset"] == 2
        assert len(body["items"]) == 2


class TestAtualizarTenant:

    def test_super_admin_atualiza_qualquer_tenant(self, client, super_admin_headers, mock_mongo):
        _seed_tenant_a(mock_mongo)
        resp = client.patch(
            "/api/tenants/tenant-A",
            headers=super_admin_headers,
            json={"nome": "Tenant A Novo", "plano": "pro"},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["nome"] == "Tenant A Novo"
        assert body["plano"] == "pro"

    def test_admin_atualiza_proprio_tenant(self, client, admin_a_headers, mock_mongo):
        _seed_tenant_a(mock_mongo)
        resp = client.patch(
            "/api/tenants/tenant-A",
            headers=admin_a_headers,
            json={"plano": "enterprise"},
        )
        assert resp.status_code == 200
        assert resp.json()["plano"] == "enterprise"

    def test_admin_nao_atualiza_outro_tenant(self, client, admin_a_headers, mock_mongo):
        mock_mongo.tenants.insert_one({
            "tenant_id": "tenant-B", "nome": "B", "plano": "free", "status": "ativo",
            "limites": {"creditos_mes": 100, "marcas_max": 1}, "branding_default": {},
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc), "audit_log": [],
        })
        resp = client.patch(
            "/api/tenants/tenant-B",
            headers=admin_a_headers,
            json={"nome": "Hackeado"},
        )
        assert resp.status_code == 403

    def test_viewer_nao_atualiza_proprio_tenant(self, client, viewer_a_headers, mock_mongo):
        _seed_tenant_a(mock_mongo)
        resp = client.patch(
            "/api/tenants/tenant-A",
            headers=viewer_a_headers,
            json={"nome": "Viewer tentou"},
        )
        assert resp.status_code == 403

    def test_tenant_inexistente_404(self, client, super_admin_headers, mock_mongo):
        resp = client.patch(
            "/api/tenants/nao-existe",
            headers=super_admin_headers,
            json={"plano": "free"},
        )
        assert resp.status_code == 404

    def test_plano_invalido_400(self, client, super_admin_headers, mock_mongo):
        _seed_tenant_a(mock_mongo)
        resp = client.patch(
            "/api/tenants/tenant-A",
            headers=super_admin_headers,
            json={"plano": "premium_mais_super"},
        )
        assert resp.status_code == 400

    def test_body_vazio_400(self, client, super_admin_headers, mock_mongo):
        _seed_tenant_a(mock_mongo)
        resp = client.patch("/api/tenants/tenant-A", headers=super_admin_headers, json={})
        assert resp.status_code == 400

    def test_auditoria_grava_de_para(self, client, super_admin_headers, mock_mongo):
        _seed_tenant_a(mock_mongo)
        client.patch(
            "/api/tenants/tenant-A",
            headers=super_admin_headers,
            json={"nome": "Renomeado"},
        )
        doc = mock_mongo.tenants.find_one({"tenant_id": "tenant-A"})
        assert any(e["action"] == "tenant_updated" for e in doc["audit_log"])
        entry = next(e for e in doc["audit_log"] if e["action"] == "tenant_updated")
        assert entry["changes"]["nome"] == {"de": "Tenant A", "para": "Renomeado"}


class TestContratoTenant:
    def test_rotas_registradas(self, client):
        paths = client.get("/openapi.json").json()["paths"]
        assert "/api/tenants" in paths
        assert "post" in paths["/api/tenants"]
        assert "get" in paths["/api/tenants"]
        assert "/api/tenants/me" in paths
        assert "/api/tenants/{tenant_id}" in paths
        assert "patch" in paths["/api/tenants/{tenant_id}"]
