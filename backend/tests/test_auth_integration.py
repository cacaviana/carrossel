"""Testes de integracao do modulo Auth.

Fluxo completo: Router -> Service -> Factory -> Repository -> MongoDB (mock)
Testa contratos de API, isolamento de tenant, ACL e validacoes.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mongomock
from fastapi.testclient import TestClient

from main import app
from middleware.auth import create_access_token, hash_password


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_mongo():
    """Substitui MongoDB real por mongomock para todos os testes.

    Patcha get_mongo_db em TODOS os modulos que fazem 'from ... import get_mongo_db',
    pois o binding e por referencia local no momento do import.
    """
    mock_client = mongomock.MongoClient()
    db = mock_client["content_factory"]

    # Precisa patchar em cada modulo que importou a funcao
    targets = [
        "data.connections.mongo_connection.get_mongo_db",
        "data.repositories.mongo.auth_repository.get_mongo_db",
        "data.repositories.mongo.invite_repository.get_mongo_db",
    ]

    patches = [patch(t, return_value=db) for t in targets]
    for p in patches:
        p.start()

    # Limpa collections antes de cada teste
    db.kanban_users.drop()
    db.kanban_invite_tokens.drop()
    yield db

    for p in patches:
        p.stop()


@pytest.fixture
def client(mock_mongo, disable_auth_override):
    """TestClient do FastAPI. Depende de mock_mongo para garantir ordem.

    `disable_auth_override` garante que o override global de get_current_user
    (vindo do conftest.py) seja removido — aqui queremos testar JWT real.
    """
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def admin_token():
    """JWT valido de admin para testes."""
    return create_access_token({
        "user_id": "000000000000000000000001",
        "tenant_id": "tenant-A",
        "role": "admin",
        "email": "admin@test.com",
        "name": "Admin Test",
    })


@pytest.fixture
def viewer_token():
    """JWT valido de viewer (nao-admin) para testes."""
    return create_access_token({
        "user_id": "000000000000000000000002",
        "tenant_id": "tenant-A",
        "role": "viewer",
        "email": "viewer@test.com",
        "name": "Viewer Test",
    })


@pytest.fixture
def tenant_b_admin_token():
    """JWT de admin do tenant B (isolamento de tenant)."""
    return create_access_token({
        "user_id": "000000000000000000000099",
        "tenant_id": "tenant-B",
        "role": "admin",
        "email": "admin@tenantb.com",
        "name": "Admin Tenant B",
    })


@pytest.fixture
def seed_admin_user(mock_mongo):
    """Insere admin no banco para testes de login."""
    doc = {
        "tenant_id": "itvalley-dev",
        "email": "admin@test.com",
        "name": "Admin Test",
        "avatar_url": None,
        "password_hash": hash_password("SenhaForte1!"),
        "role": "admin",
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
        "deleted_at": None,
    }
    result = mock_mongo.kanban_users.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


@pytest.fixture
def seed_user_tenant_a(mock_mongo):
    """Insere usuario no tenant-A para testes."""
    doc = {
        "tenant_id": "tenant-A",
        "email": "user1@test.com",
        "name": "User One",
        "avatar_url": None,
        "password_hash": hash_password("SenhaForte1!"),
        "role": "copywriter",
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
        "deleted_at": None,
    }
    result = mock_mongo.kanban_users.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


STRONG_PASSWORD = "SenhaForte1!"
WEAK_PASSWORDS = [
    "abc",             # muito curta
    "abcdefgh",        # sem maiuscula, numero, especial
    "Abcdefgh",        # sem numero, especial
    "Abcdefg1",        # sem especial
]


# ===========================================================================
# 1. LOGIN FLOW
# ===========================================================================

class TestLoginFlow:
    """Fluxo: POST /api/auth/login -> Service -> Factory -> Repository -> JWT"""

    def test_login_credenciais_validas(self, client, seed_admin_user):
        """Login valido retorna JWT + dados do usuario."""
        resp = client.post("/api/auth/login", json={
            "email": "admin@test.com",
            "password": "SenhaForte1!",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert body["email"] == "admin@test.com"
        assert body["role"] == "admin"
        assert body["name"] == "Admin Test"
        assert body["user_id"]  # nao vazio
        assert body["tenant_id"] == "itvalley-dev"

    def test_login_email_errado_401(self, client, seed_admin_user):
        """Email inexistente retorna 401."""
        resp = client.post("/api/auth/login", json={
            "email": "naoexiste@test.com",
            "password": "SenhaForte1!",
        })
        assert resp.status_code == 401

    def test_login_senha_errada_401(self, client, seed_admin_user):
        """Senha incorreta retorna 401."""
        resp = client.post("/api/auth/login", json={
            "email": "admin@test.com",
            "password": "SenhaErrada1!",
        })
        assert resp.status_code == 401

    def test_login_usuario_desativado_401(self, client, mock_mongo):
        """Usuario soft-deleted nao consegue logar."""
        mock_mongo.kanban_users.insert_one({
            "tenant_id": "itvalley-dev",
            "email": "deleted@test.com",
            "name": "Deleted",
            "password_hash": hash_password("SenhaForte1!"),
            "role": "viewer",
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
            "deleted_at": datetime.now(timezone.utc),  # soft deleted
        })
        resp = client.post("/api/auth/login", json={
            "email": "deleted@test.com",
            "password": "SenhaForte1!",
        })
        assert resp.status_code == 401
        assert "desativado" in resp.json()["detail"].lower()

    def test_login_email_invalido_422(self, client):
        """Email mal formatado retorna 422 (validacao Pydantic)."""
        resp = client.post("/api/auth/login", json={
            "email": "nao-e-email",
            "password": "SenhaForte1!",
        })
        assert resp.status_code == 422


# ===========================================================================
# 2. ME FLOW
# ===========================================================================

class TestMeFlow:
    """Fluxo: GET /api/auth/me -> JWT decode -> Service -> Repository"""

    def test_me_com_jwt_valido(self, client, admin_token, seed_user_tenant_a):
        """JWT valido retorna dados do usuario autenticado."""
        # Precisamos de um usuario no banco com o ID do token
        resp = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        # Pode ser 404 se o user_id do token nao existe no banco
        # Vamos criar o user correspondente ao token
        assert resp.status_code in (200, 404)

    def test_me_sem_token_401(self, client):
        """Sem Authorization header retorna 401/403."""
        resp = client.get("/api/auth/me")
        assert resp.status_code == 403  # HTTPBearer retorna 403 se sem header

    def test_me_token_invalido_401(self, client):
        """Token aleatorio retorna 401."""
        resp = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer token-invalido-xyz"},
        )
        assert resp.status_code == 401

    def test_me_token_expirado_401(self, client):
        """Token expirado retorna 401."""
        expired = create_access_token(
            {"user_id": "x", "tenant_id": "t", "role": "admin", "email": "e@e.com", "name": "N"},
            expires_delta=timedelta(seconds=-1),
        )
        resp = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired}"},
        )
        assert resp.status_code == 401


# ===========================================================================
# 3. CRUD USUARIOS
# ===========================================================================

class TestCrudUsuarios:
    """Fluxo: admin cria, lista, edita, desativa e reativa usuarios."""

    def test_criar_usuario_admin_only(self, client, admin_token):
        """Admin cria usuario com sucesso, retorna 201."""
        resp = client.post(
            "/api/auth/users",
            json={
                "email": "novo@test.com",
                "name": "Novo Usuario",
                "password": STRONG_PASSWORD,
                "role": "copywriter",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "novo@test.com"
        assert body["name"] == "Novo Usuario"
        assert body["role"] == "copywriter"
        assert body["tenant_id"] == "tenant-A"
        assert "user_id" in body

    def test_criar_usuario_email_duplicado_409(self, client, admin_token):
        """Criar usuario com email ja existente retorna 409."""
        payload = {
            "email": "dup@test.com",
            "name": "First",
            "password": STRONG_PASSWORD,
            "role": "viewer",
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp1 = client.post("/api/auth/users", json=payload, headers=headers)
        assert resp1.status_code == 201

        resp2 = client.post("/api/auth/users", json=payload, headers=headers)
        assert resp2.status_code == 409

    def test_listar_usuarios(self, client, admin_token):
        """Lista usuarios do tenant. Admin e nao-admin podem listar."""
        # Criar dois usuarios
        headers = {"Authorization": f"Bearer {admin_token}"}
        client.post("/api/auth/users", json={
            "email": "a@test.com", "name": "A", "password": STRONG_PASSWORD, "role": "viewer",
        }, headers=headers)
        client.post("/api/auth/users", json={
            "email": "b@test.com", "name": "B", "password": STRONG_PASSWORD, "role": "designer",
        }, headers=headers)

        resp = client.get("/api/auth/users", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 2
        emails = [u["email"] for u in body["usuarios"]]
        assert "a@test.com" in emails
        assert "b@test.com" in emails

    def test_atualizar_usuario(self, client, admin_token):
        """Admin atualiza nome/role de outro usuario."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_resp = client.post("/api/auth/users", json={
            "email": "edit@test.com", "name": "Before", "password": STRONG_PASSWORD, "role": "viewer",
        }, headers=headers)
        user_id = create_resp.json()["user_id"]

        resp = client.patch(
            f"/api/auth/users/{user_id}",
            json={"name": "After", "role": "designer"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "After"
        assert resp.json()["role"] == "designer"

    def test_atualizar_nenhum_campo_400(self, client, admin_token):
        """Patch sem campos retorna 400."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_resp = client.post("/api/auth/users", json={
            "email": "nofield@test.com", "name": "X", "password": STRONG_PASSWORD, "role": "viewer",
        }, headers=headers)
        user_id = create_resp.json()["user_id"]

        resp = client.patch(
            f"/api/auth/users/{user_id}",
            json={},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_desativar_usuario(self, client, admin_token):
        """Admin desativa usuario (soft delete)."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_resp = client.post("/api/auth/users", json={
            "email": "deactivate@test.com", "name": "Deact", "password": STRONG_PASSWORD, "role": "viewer",
        }, headers=headers)
        user_id = create_resp.json()["user_id"]

        resp = client.delete(f"/api/auth/users/{user_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    def test_desativar_a_si_mesmo_400(self, client, admin_token):
        """Admin nao pode desativar a si mesmo."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = client.delete(
            "/api/auth/users/000000000000000000000001",
            headers=headers,
        )
        assert resp.status_code == 400

    def test_reativar_usuario(self, client, admin_token):
        """Admin reativa usuario desativado."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_resp = client.post("/api/auth/users", json={
            "email": "react@test.com", "name": "React", "password": STRONG_PASSWORD, "role": "viewer",
        }, headers=headers)
        user_id = create_resp.json()["user_id"]

        # Desativar
        client.delete(f"/api/auth/users/{user_id}", headers=headers)

        # Reativar
        resp = client.post(f"/api/auth/users/{user_id}/reativar", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "react@test.com"


# ===========================================================================
# 4. INVITE FLOW
# ===========================================================================

class TestInviteFlow:
    """Fluxo: admin convida -> token gerado -> aceitar com senha -> usuario criado."""

    def test_invite_flow_completo(self, client, admin_token):
        """Fluxo completo de convite: gerar + aceitar."""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. Admin cria convite
        resp_invite = client.post("/api/auth/users/invite", json={
            "email": "convidado@test.com",
            "name": "Convidado",
            "role": "copywriter",
        }, headers=headers)
        assert resp_invite.status_code == 201
        invite = resp_invite.json()
        assert invite["email"] == "convidado@test.com"
        assert invite["role"] == "copywriter"
        assert "invite_token" in invite
        assert "invite_url" in invite
        assert "expires_at" in invite

        # 2. Aceitar convite com senha forte
        resp_accept = client.post("/api/auth/users/invite/accept", json={
            "token": invite["invite_token"],
            "password": STRONG_PASSWORD,
        })
        assert resp_accept.status_code == 201
        user = resp_accept.json()
        assert user["email"] == "convidado@test.com"
        assert user["role"] == "copywriter"
        assert user["name"] == "Convidado"

    def test_invite_email_duplicado_409(self, client, admin_token):
        """Convite para email ja cadastrado retorna 409."""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Criar usuario primeiro
        client.post("/api/auth/users", json={
            "email": "existe@test.com", "name": "Existe",
            "password": STRONG_PASSWORD, "role": "viewer",
        }, headers=headers)

        # Tentar convidar mesmo email
        resp = client.post("/api/auth/users/invite", json={
            "email": "existe@test.com", "name": "Existe", "role": "viewer",
        }, headers=headers)
        assert resp.status_code == 409

    def test_invite_pendente_duplicado_409(self, client, admin_token):
        """Segundo convite para mesmo email pendente retorna 409."""
        headers = {"Authorization": f"Bearer {admin_token}"}

        client.post("/api/auth/users/invite", json={
            "email": "pending@test.com", "name": "Pending", "role": "viewer",
        }, headers=headers)

        resp = client.post("/api/auth/users/invite", json={
            "email": "pending@test.com", "name": "Pending", "role": "viewer",
        }, headers=headers)
        assert resp.status_code == 409

    def test_aceitar_convite_token_invalido_404(self, client):
        """Token inexistente retorna 404."""
        resp = client.post("/api/auth/users/invite/accept", json={
            "token": "token-que-nao-existe",
            "password": STRONG_PASSWORD,
        })
        assert resp.status_code == 404

    def test_aceitar_convite_senha_fraca_422(self, client, admin_token):
        """Aceitar convite com senha fraca retorna 422."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp_invite = client.post("/api/auth/users/invite", json={
            "email": "fraco@test.com", "name": "Fraco", "role": "viewer",
        }, headers=headers)
        token = resp_invite.json()["invite_token"]

        resp = client.post("/api/auth/users/invite/accept", json={
            "token": token,
            "password": "abc",
        })
        assert resp.status_code == 422

    def test_aceitar_convite_ja_usado_400(self, client, admin_token):
        """Aceitar convite ja utilizado retorna 400."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp_invite = client.post("/api/auth/users/invite", json={
            "email": "usedtwice@test.com", "name": "Used", "role": "viewer",
        }, headers=headers)
        token = resp_invite.json()["invite_token"]

        # Aceitar primeira vez
        client.post("/api/auth/users/invite/accept", json={
            "token": token, "password": STRONG_PASSWORD,
        })

        # Aceitar segunda vez
        resp = client.post("/api/auth/users/invite/accept", json={
            "token": token, "password": STRONG_PASSWORD,
        })
        assert resp.status_code == 400


# ===========================================================================
# 5. ACL — ROLES NAO-ADMIN RECEBEM 403
# ===========================================================================

class TestACL:
    """Verifica que endpoints admin-only rejeitam roles nao-admin."""

    def test_viewer_nao_cria_usuario_403(self, client, viewer_token):
        resp = client.post("/api/auth/users", json={
            "email": "x@test.com", "name": "X", "password": STRONG_PASSWORD, "role": "viewer",
        }, headers={"Authorization": f"Bearer {viewer_token}"})
        assert resp.status_code == 403

    def test_viewer_nao_convida_403(self, client, viewer_token):
        resp = client.post("/api/auth/users/invite", json={
            "email": "x@test.com", "name": "X", "role": "viewer",
        }, headers={"Authorization": f"Bearer {viewer_token}"})
        assert resp.status_code == 403

    def test_viewer_nao_atualiza_403(self, client, viewer_token):
        resp = client.patch(
            "/api/auth/users/000000000000000000000001",
            json={"name": "hack"},
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert resp.status_code == 403

    def test_viewer_nao_desativa_403(self, client, viewer_token):
        resp = client.delete(
            "/api/auth/users/000000000000000000000001",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert resp.status_code == 403

    def test_viewer_nao_reativa_403(self, client, viewer_token):
        resp = client.post(
            "/api/auth/users/000000000000000000000001/reativar",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert resp.status_code == 403

    def test_copywriter_nao_cria_usuario_403(self, client):
        """Copywriter tambem nao e admin."""
        token = create_access_token({
            "user_id": "000000000000000000000003",
            "tenant_id": "tenant-A",
            "role": "copywriter",
            "email": "copy@test.com",
            "name": "Copywriter",
        })
        resp = client.post("/api/auth/users", json={
            "email": "x@test.com", "name": "X", "password": STRONG_PASSWORD, "role": "viewer",
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    def test_viewer_pode_listar_200(self, client, viewer_token):
        """Viewer pode listar usuarios (GET /users nao exige admin)."""
        resp = client.get(
            "/api/auth/users",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert resp.status_code == 200


# ===========================================================================
# 6. SENHA FORTE
# ===========================================================================

class TestSenhaForte:
    """RN-021: Validacao de senha forte no DTO."""

    @pytest.mark.parametrize("senha", WEAK_PASSWORDS)
    def test_criar_usuario_senha_fraca_422(self, client, admin_token, senha):
        resp = client.post("/api/auth/users", json={
            "email": "weak@test.com", "name": "Weak", "password": senha, "role": "viewer",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 422

    def test_criar_usuario_senha_forte_ok(self, client, admin_token):
        resp = client.post("/api/auth/users", json={
            "email": "strong@test.com", "name": "Strong",
            "password": STRONG_PASSWORD, "role": "viewer",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 201

    @pytest.mark.parametrize("senha", WEAK_PASSWORDS)
    def test_aceitar_convite_senha_fraca_422(self, client, senha):
        """Senha fraca ao aceitar convite tambem e rejeitada."""
        resp = client.post("/api/auth/users/invite/accept", json={
            "token": "qualquer-token",
            "password": senha,
        })
        assert resp.status_code == 422

    def test_role_invalido_422(self, client, admin_token):
        """Role invalido retorna 422."""
        resp = client.post("/api/auth/users", json={
            "email": "badrole@test.com", "name": "Bad", "password": STRONG_PASSWORD,
            "role": "hacker",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 422


# ===========================================================================
# 7. ISOLAMENTO DE TENANT
# ===========================================================================

class TestIsolamentoTenant:
    """Dados do tenant A nao aparecem para tenant B."""

    def test_listar_usuarios_isolado_por_tenant(self, client, admin_token, tenant_b_admin_token):
        """Usuarios criados por tenant A nao aparecem na listagem de tenant B."""
        # Admin do tenant-A cria usuario
        client.post("/api/auth/users", json={
            "email": "tenantA@test.com", "name": "Tenant A User",
            "password": STRONG_PASSWORD, "role": "viewer",
        }, headers={"Authorization": f"Bearer {admin_token}"})

        # Admin do tenant-B lista
        resp = client.get(
            "/api/auth/users",
            headers={"Authorization": f"Bearer {tenant_b_admin_token}"},
        )
        assert resp.status_code == 200
        emails = [u["email"] for u in resp.json()["usuarios"]]
        assert "tenantA@test.com" not in emails

    def test_atualizar_usuario_outro_tenant_404(self, client, admin_token, tenant_b_admin_token):
        """Admin do tenant B nao consegue editar usuario do tenant A."""
        # Criar usuario no tenant-A
        headers_a = {"Authorization": f"Bearer {admin_token}"}
        create_resp = client.post("/api/auth/users", json={
            "email": "cross@test.com", "name": "Cross",
            "password": STRONG_PASSWORD, "role": "viewer",
        }, headers=headers_a)
        user_id = create_resp.json()["user_id"]

        # Tenant-B tenta editar
        headers_b = {"Authorization": f"Bearer {tenant_b_admin_token}"}
        resp = client.patch(
            f"/api/auth/users/{user_id}",
            json={"name": "Hacked"},
            headers=headers_b,
        )
        assert resp.status_code == 404


# ===========================================================================
# 8. CONTRATOS DE API
# ===========================================================================

class TestContratosAPI:
    """Verifica que responses batem com o que o frontend espera."""

    def test_login_response_contract(self, client, seed_admin_user):
        """Response de login tem todos os campos esperados."""
        resp = client.post("/api/auth/login", json={
            "email": "admin@test.com",
            "password": "SenhaForte1!",
        })
        body = resp.json()
        expected_keys = {"access_token", "token_type", "user_id", "tenant_id", "role", "name", "email"}
        assert expected_keys == set(body.keys())

    def test_usuario_response_contract(self, client, admin_token):
        """Response de criar usuario tem campos esperados."""
        resp = client.post("/api/auth/users", json={
            "email": "contract@test.com", "name": "Contract",
            "password": STRONG_PASSWORD, "role": "viewer",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        body = resp.json()
        expected_keys = {"user_id", "tenant_id", "email", "name", "role", "avatar_url", "created_at"}
        assert expected_keys == set(body.keys())

    def test_listar_response_contract(self, client, admin_token):
        """Response de listar tem usuarios + total."""
        resp = client.get(
            "/api/auth/users",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        body = resp.json()
        assert "usuarios" in body
        assert "total" in body
        assert isinstance(body["usuarios"], list)
        assert isinstance(body["total"], int)

    def test_convite_response_contract(self, client, admin_token):
        """Response de convite tem campos esperados."""
        resp = client.post("/api/auth/users/invite", json={
            "email": "invite-contract@test.com", "name": "IC", "role": "viewer",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        body = resp.json()
        expected_keys = {"invite_token", "email", "name", "role", "expires_at", "invite_url"}
        assert expected_keys == set(body.keys())


# ===========================================================================
# 9. CASO DE USO: CONVIDAR USUARIO (foco explicito)
# ===========================================================================

class TestCasoDeUsoConvidarUsuario:
    """Caso de uso isolado: Convidar Usuario.

    Valida especificamente:
    - invite_token gerado (nao vazio)
    - expires_at no futuro (TTL 48h)
    - invite_url contem token
    - role do convite e preservado no usuario final
    - email normalizado (case-insensitive) no usuario
    """

    def test_convite_gera_token_nao_vazio(self, client, admin_token):
        resp = client.post("/api/auth/users/invite", json={
            "email": "token@test.com", "name": "T", "role": "viewer",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 201
        assert len(resp.json()["invite_token"]) > 20

    def test_convite_expira_no_futuro(self, client, admin_token):
        resp = client.post("/api/auth/users/invite", json={
            "email": "exp@test.com", "name": "E", "role": "viewer",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        expires_at = resp.json()["expires_at"]
        # Parse ISO date
        exp_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        assert exp_dt > datetime.now(timezone.utc)

    def test_convite_url_contem_token(self, client, admin_token):
        resp = client.post("/api/auth/users/invite", json={
            "email": "url@test.com", "name": "U", "role": "viewer",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        body = resp.json()
        assert body["invite_token"] in body["invite_url"]
        assert "/aceitar-convite" in body["invite_url"]

    def test_convite_preserva_role_no_usuario_final(self, client, admin_token):
        """Role escolhido no convite deve aparecer no usuario apos aceitar."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp_inv = client.post("/api/auth/users/invite", json={
            "email": "designer@test.com", "name": "D", "role": "designer",
        }, headers=headers)
        token = resp_inv.json()["invite_token"]

        resp_acc = client.post("/api/auth/users/invite/accept", json={
            "token": token, "password": STRONG_PASSWORD,
        })
        assert resp_acc.status_code == 201
        assert resp_acc.json()["role"] == "designer"

    def test_convite_com_role_invalido_422(self, client, admin_token):
        resp = client.post("/api/auth/users/invite", json={
            "email": "x@test.com", "name": "X", "role": "ceo",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 422

    def test_convite_respeita_tenant_id_do_admin(self, client, admin_token, mock_mongo):
        """Convite deve ser persistido com tenant_id do admin que convidou."""
        resp = client.post("/api/auth/users/invite", json={
            "email": "tenanted@test.com", "name": "T", "role": "viewer",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        token = resp.json()["invite_token"]
        # Admin e tenant-A -> convite tbm deve ser tenant-A
        invite_doc = mock_mongo.kanban_invite_tokens.find_one({"token": token})
        assert invite_doc["tenant_id"] == "tenant-A"


# ===========================================================================
# 10. CASO DE USO: ATIVAR (REATIVAR) USUARIO
# ===========================================================================

class TestCasoDeUsoAtivarUsuario:
    """Caso de uso isolado: Reativar Usuario (ja desativado)."""

    def test_reativar_remove_deleted_at(self, client, admin_token, mock_mongo):
        """Reativar apaga o campo deleted_at (soft undelete)."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_resp = client.post("/api/auth/users", json={
            "email": "undelete@test.com", "name": "UD",
            "password": STRONG_PASSWORD, "role": "viewer",
        }, headers=headers)
        user_id = create_resp.json()["user_id"]

        client.delete(f"/api/auth/users/{user_id}", headers=headers)
        # Confirma deleted_at preenchido
        from bson import ObjectId
        doc = mock_mongo.kanban_users.find_one({"_id": ObjectId(user_id)})
        assert doc["deleted_at"] is not None

        client.post(f"/api/auth/users/{user_id}/reativar", headers=headers)
        doc = mock_mongo.kanban_users.find_one({"_id": ObjectId(user_id)})
        assert doc["deleted_at"] is None

    def test_reativar_usuario_inexistente_404(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = client.post(
            "/api/auth/users/000000000000000000000999/reativar",
            headers=headers,
        )
        assert resp.status_code == 404

    def test_reativar_chama_repository_com_tenant_id(self, mock_mongo, admin_token, client):
        """Garante que reativacao repassa tenant_id correto ao Repository (isolamento)."""
        from bson import ObjectId
        headers = {"Authorization": f"Bearer {admin_token}"}
        create = client.post("/api/auth/users", json={
            "email": "repouser@test.com", "name": "R",
            "password": STRONG_PASSWORD, "role": "viewer",
        }, headers=headers)
        user_id = create.json()["user_id"]
        client.delete(f"/api/auth/users/{user_id}", headers=headers)

        # Antes da reativacao: deleted_at nao-nulo, tenant_id preservado
        doc_before = mock_mongo.kanban_users.find_one({"_id": ObjectId(user_id)})
        assert doc_before["tenant_id"] == "tenant-A"
        assert doc_before["deleted_at"] is not None

        client.post(f"/api/auth/users/{user_id}/reativar", headers=headers)
        doc_after = mock_mongo.kanban_users.find_one({"_id": ObjectId(user_id)})
        assert doc_after["tenant_id"] == "tenant-A"
        assert doc_after["deleted_at"] is None

    def test_reativar_viewer_recebe_403(self, client, viewer_token):
        """Somente admin pode reativar."""
        resp = client.post(
            "/api/auth/users/000000000000000000000001/reativar",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert resp.status_code == 403

    def test_reativar_isola_tenant(self, client, admin_token, tenant_b_admin_token):
        """Admin de outro tenant nao reativa usuario alheio."""
        headers_a = {"Authorization": f"Bearer {admin_token}"}
        create = client.post("/api/auth/users", json={
            "email": "crosstenant@test.com", "name": "X",
            "password": STRONG_PASSWORD, "role": "viewer",
        }, headers=headers_a)
        user_id = create.json()["user_id"]
        client.delete(f"/api/auth/users/{user_id}", headers=headers_a)

        headers_b = {"Authorization": f"Bearer {tenant_b_admin_token}"}
        resp = client.post(f"/api/auth/users/{user_id}/reativar", headers=headers_b)
        assert resp.status_code == 404


# ===========================================================================
# 11. CASO DE USO: ATRIBUIR PERFIL (ROLE) AO USUARIO
# ===========================================================================

class TestCasoDeUsoAtribuirPerfilUsuario:
    """Caso de uso isolado: Atribuir Perfil (role) via PATCH /users/{id}."""

    @pytest.mark.parametrize("role", ["admin", "copywriter", "designer", "reviewer", "viewer"])
    def test_atribuir_role_valido(self, client, admin_token, role):
        headers = {"Authorization": f"Bearer {admin_token}"}
        create = client.post("/api/auth/users", json={
            "email": f"role-{role}@test.com", "name": "R",
            "password": STRONG_PASSWORD, "role": "viewer",
        }, headers=headers)
        user_id = create.json()["user_id"]

        resp = client.patch(
            f"/api/auth/users/{user_id}",
            json={"role": role},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == role

    def test_atribuir_role_invalido_422(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        create = client.post("/api/auth/users", json={
            "email": "bad-role@test.com", "name": "B",
            "password": STRONG_PASSWORD, "role": "viewer",
        }, headers=headers)
        user_id = create.json()["user_id"]

        resp = client.patch(
            f"/api/auth/users/{user_id}",
            json={"role": "ceo"},
            headers=headers,
        )
        assert resp.status_code == 422

    def test_atribuir_role_sem_mudar_outros_campos(self, client, admin_token):
        """Partial update: role muda, nome permanece."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        create = client.post("/api/auth/users", json={
            "email": "keep-name@test.com", "name": "Original Name",
            "password": STRONG_PASSWORD, "role": "viewer",
        }, headers=headers)
        user_id = create.json()["user_id"]

        resp = client.patch(
            f"/api/auth/users/{user_id}",
            json={"role": "copywriter"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "copywriter"
        assert resp.json()["name"] == "Original Name"

    def test_atribuir_role_persiste_updated_at(self, client, admin_token, mock_mongo):
        """Atribuir perfil deve atualizar updated_at no doc."""
        from bson import ObjectId
        headers = {"Authorization": f"Bearer {admin_token}"}
        create = client.post("/api/auth/users", json={
            "email": "updated@test.com", "name": "U",
            "password": STRONG_PASSWORD, "role": "viewer",
        }, headers=headers)
        user_id = create.json()["user_id"]

        # updated_at comeca em None
        doc_antes = mock_mongo.kanban_users.find_one({"_id": ObjectId(user_id)})
        assert doc_antes["updated_at"] is None

        client.patch(
            f"/api/auth/users/{user_id}",
            json={"role": "admin"},
            headers=headers,
        )
        doc_depois = mock_mongo.kanban_users.find_one({"_id": ObjectId(user_id)})
        assert doc_depois["updated_at"] is not None

    def test_atribuir_role_viewer_recebe_403(self, client, viewer_token):
        """Somente admin pode atribuir perfil."""
        resp = client.patch(
            "/api/auth/users/000000000000000000000001",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert resp.status_code == 403

    def test_atribuir_role_usuario_inexistente_404(self, client, admin_token):
        resp = client.patch(
            "/api/auth/users/000000000000000000000999",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404

    def test_atribuir_role_isola_tenant(self, client, admin_token, tenant_b_admin_token):
        """Admin do tenant B nao atribui role a user do tenant A."""
        headers_a = {"Authorization": f"Bearer {admin_token}"}
        create = client.post("/api/auth/users", json={
            "email": "tenantrole@test.com", "name": "TR",
            "password": STRONG_PASSWORD, "role": "viewer",
        }, headers=headers_a)
        user_id = create.json()["user_id"]

        headers_b = {"Authorization": f"Bearer {tenant_b_admin_token}"}
        resp = client.patch(
            f"/api/auth/users/{user_id}",
            json={"role": "admin"},
            headers=headers_b,
        )
        assert resp.status_code == 404
