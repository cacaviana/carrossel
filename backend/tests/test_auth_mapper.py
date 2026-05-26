"""Testes unitarios — mappers/auth_mapper.py

Cobre: todas as conversoes doc -> response.
"""

import sys, os
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bson import ObjectId
from mappers.auth_mapper import AuthMapper


def _make_user_doc(**overrides):
    doc = {
        "_id": ObjectId(),
        "tenant_id": "t1",
        "email": "user@test.com",
        "name": "Test User",
        "role": "admin",
        "avatar_url": "http://avatar.png",
        "password_hash": "hashed",
        "created_at": datetime(2025, 1, 1, tzinfo=timezone.utc),
        "updated_at": None,
        "deleted_at": None,
    }
    doc.update(overrides)
    return doc


class TestToLoginResponse:
    def test_mapeia_campos_corretamente(self):
        doc = _make_user_doc()
        resp = AuthMapper.to_login_response(doc, "jwt-token-xyz")
        assert resp.access_token == "jwt-token-xyz"
        assert resp.token_type == "bearer"
        assert resp.user_id == str(doc["_id"])
        assert resp.tenant_id == "t1"
        assert resp.role == "admin"
        assert resp.name == "Test User"
        assert resp.email == "user@test.com"


class TestToUsuarioResponse:
    def test_mapeia_campos_corretamente(self):
        doc = _make_user_doc()
        resp = AuthMapper.to_usuario_response(doc)
        assert resp.user_id == str(doc["_id"])
        assert resp.avatar_url == "http://avatar.png"
        assert resp.created_at == datetime(2025, 1, 1, tzinfo=timezone.utc)

    def test_avatar_url_none_quando_ausente(self):
        doc = _make_user_doc(avatar_url=None)
        resp = AuthMapper.to_usuario_response(doc)
        assert resp.avatar_url is None


class TestToMeResponse:
    def test_mapeia_campos_corretamente(self):
        doc = _make_user_doc()
        resp = AuthMapper.to_me_response(doc)
        assert resp.user_id == str(doc["_id"])
        assert resp.role == "admin"
        assert resp.avatar_url == "http://avatar.png"


class TestToConviteResponse:
    def test_mapeia_campos_e_gera_url(self):
        invite = {
            "token": "tok123",
            "email": "a@b.c",
            "name": "Guest",
            "role": "viewer",
            "expires_at": datetime(2025, 6, 1, tzinfo=timezone.utc),
        }
        resp = AuthMapper.to_convite_response(invite, "http://localhost:5173")
        assert resp.invite_token == "tok123"
        assert resp.invite_url == "http://localhost:5173/aceitar-convite?token=tok123"
        assert resp.role == "viewer"


class TestToUsuarioItem:
    def test_mapeia_item(self):
        doc = _make_user_doc()
        item = AuthMapper.to_usuario_item(doc)
        assert item.user_id == str(doc["_id"])
        assert item.deleted_at is None


class TestToListarResponse:
    def test_lista_vazia(self):
        resp = AuthMapper.to_listar_response([])
        assert resp.total == 0
        assert resp.usuarios == []

    def test_lista_com_itens(self):
        docs = [_make_user_doc(), _make_user_doc(name="Outro")]
        resp = AuthMapper.to_listar_response(docs)
        assert resp.total == 2
        assert len(resp.usuarios) == 2
