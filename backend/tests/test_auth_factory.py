"""Testes unitarios — factories/auth_factory.py

Cobre: validate_login, create_user_doc, create_invite_doc,
       create_user_from_invite (invite 48h TTL), build_update_fields.
"""

import sys, os
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi import HTTPException

from factories.auth_factory import AuthFactory
from middleware.auth import hash_password


# ===================================================================
# validate_login
# ===================================================================
class TestValidateLogin:
    def _make_user_doc(self, password: str = "Abc123!@", deleted: bool = False):
        return {
            "_id": "u1",
            "tenant_id": "t1",
            "email": "a@b.c",
            "name": "Test",
            "password_hash": hash_password(password),
            "role": "admin",
            "deleted_at": datetime.now(timezone.utc) if deleted else None,
        }

    def test_aceita_credenciais_corretas(self):
        doc = self._make_user_doc()
        result = AuthFactory.validate_login("a@b.c", "Abc123!@", doc)
        assert result["email"] == "a@b.c"

    def test_rejeita_usuario_inexistente(self):
        with pytest.raises(HTTPException) as exc:
            AuthFactory.validate_login("a@b.c", "Abc123!@", None)
        assert exc.value.status_code == 401

    def test_rejeita_usuario_deletado(self):
        doc = self._make_user_doc(deleted=True)
        with pytest.raises(HTTPException) as exc:
            AuthFactory.validate_login("a@b.c", "Abc123!@", doc)
        assert exc.value.status_code == 401
        assert "desativado" in exc.value.detail.lower()

    def test_rejeita_senha_errada(self):
        doc = self._make_user_doc()
        with pytest.raises(HTTPException) as exc:
            AuthFactory.validate_login("a@b.c", "SenhaErrada1!", doc)
        assert exc.value.status_code == 401


# ===================================================================
# create_user_doc
# ===================================================================
class TestCreateUserDoc:
    def test_cria_documento_com_campos_corretos(self):
        dto = SimpleNamespace(
            email="User@Test.COM", name="Test User", password="Abc123!@", role="designer"
        )
        doc = AuthFactory.create_user_doc(dto, tenant_id="t1")
        assert doc["tenant_id"] == "t1"
        assert doc["email"] == "user@test.com"  # lowercase
        assert doc["name"] == "Test User"
        assert doc["role"] == "designer"
        assert doc["password_hash"] != "Abc123!@"  # hasheada
        assert doc["deleted_at"] is None
        assert doc["updated_at"] is None
        assert isinstance(doc["created_at"], datetime)

    def test_email_convertido_para_lowercase(self):
        dto = SimpleNamespace(
            email="ADMIN@ITVALLEY.COM", name="A", password="Abc123!@", role="admin"
        )
        doc = AuthFactory.create_user_doc(dto, tenant_id="t1")
        assert doc["email"] == "admin@itvalley.com"


# ===================================================================
# create_invite_doc — 48h TTL
# ===================================================================
class TestCreateInviteDoc:
    def test_cria_convite_com_token(self):
        dto = SimpleNamespace(email="a@b.c", name="Guest", role="viewer")
        doc = AuthFactory.create_invite_doc(dto, tenant_id="t1", created_by="admin1")
        assert len(doc["token"]) > 20  # token_urlsafe(32) gera ~43 chars
        assert doc["tenant_id"] == "t1"
        assert doc["created_by"] == "admin1"
        assert doc["used"] is False

    def test_expira_em_48h(self):
        dto = SimpleNamespace(email="a@b.c", name="Guest", role="viewer")
        doc = AuthFactory.create_invite_doc(dto, tenant_id="t1", created_by="admin1")
        diff = doc["expires_at"] - doc["created_at"]
        assert timedelta(hours=47, minutes=55) < diff < timedelta(hours=48, minutes=5)

    def test_tokens_diferentes_a_cada_chamada(self):
        dto = SimpleNamespace(email="a@b.c", name="Guest", role="viewer")
        doc1 = AuthFactory.create_invite_doc(dto, "t1", "admin1")
        doc2 = AuthFactory.create_invite_doc(dto, "t1", "admin1")
        assert doc1["token"] != doc2["token"]


# ===================================================================
# create_user_from_invite
# ===================================================================
class TestCreateUserFromInvite:
    def _make_invite(self, used=False, expired=False):
        expires = datetime.now(timezone.utc) + (
            timedelta(hours=-1) if expired else timedelta(hours=24)
        )
        return {
            "tenant_id": "t1",
            "email": "Guest@B.C",
            "name": "Guest",
            "role": "copywriter",
            "token": "tok123",
            "used": used,
            "expires_at": expires,
        }

    def test_cria_usuario_a_partir_de_convite_valido(self):
        invite = self._make_invite()
        doc = AuthFactory.create_user_from_invite(invite, "Abc123!@")
        assert doc["tenant_id"] == "t1"
        assert doc["email"] == "guest@b.c"  # lowercase
        assert doc["role"] == "copywriter"
        assert doc["password_hash"] != "Abc123!@"

    def test_rejeita_convite_ja_usado(self):
        invite = self._make_invite(used=True)
        with pytest.raises(HTTPException) as exc:
            AuthFactory.create_user_from_invite(invite, "Abc123!@")
        assert exc.value.status_code == 400
        assert "utilizado" in exc.value.detail.lower()

    def test_rejeita_convite_expirado(self):
        invite = self._make_invite(expired=True)
        with pytest.raises(HTTPException) as exc:
            AuthFactory.create_user_from_invite(invite, "Abc123!@")
        assert exc.value.status_code == 400
        assert "expirado" in exc.value.detail.lower()


# ===================================================================
# build_update_fields
# ===================================================================
class TestBuildUpdateFields:
    def test_partial_update_so_name(self):
        dto = SimpleNamespace(name="Novo", role=None, avatar_url=None)
        updates = AuthFactory.build_update_fields(dto)
        assert updates["name"] == "Novo"
        assert "role" not in updates
        assert "updated_at" in updates

    def test_nenhum_campo_retorna_vazio(self):
        dto = SimpleNamespace(name=None, role=None, avatar_url=None)
        updates = AuthFactory.build_update_fields(dto)
        assert updates == {}

    def test_todos_campos(self):
        dto = SimpleNamespace(name="N", role="admin", avatar_url="http://img.png")
        updates = AuthFactory.build_update_fields(dto)
        assert "name" in updates
        assert "role" in updates
        assert "avatar_url" in updates
        assert "updated_at" in updates
