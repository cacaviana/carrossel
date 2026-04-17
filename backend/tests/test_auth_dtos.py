"""Testes unitarios — DTOs do dominio Auth.

Cobre: validacoes Pydantic, senha forte (RN-021), role valido, campos obrigatorios.
"""

import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pydantic import ValidationError

from dtos.auth.login.request import LoginRequest
from dtos.auth.login.response import LoginResponse
from dtos.auth.criar_usuario.request import CriarUsuarioRequest
from dtos.auth.criar_usuario.response import UsuarioResponse
from dtos.auth.convidar_usuario.request import ConvidarUsuarioRequest
from dtos.auth.convidar_usuario.response import ConviteResponse
from dtos.auth.aceitar_convite.request import AceitarConviteRequest
from dtos.auth.atualizar_usuario.request import AtualizarUsuarioRequest
from dtos.auth.me.response import MeResponse
from dtos.auth.listar_usuarios.response import UsuarioItem, ListarUsuariosResponse


# ===================================================================
# LoginRequest
# ===================================================================
class TestLoginRequest:
    def test_cria_com_campos_validos(self):
        req = LoginRequest(email="user@test.com", password="Abc123!@")
        assert req.email == "user@test.com"

    def test_rejeita_email_invalido(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="nao-e-email", password="Abc123!@")

    def test_campo_password_obrigatorio(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="user@test.com")


# ===================================================================
# CriarUsuarioRequest — RN-021 senha forte
# ===================================================================
class TestCriarUsuarioRequest:
    def test_aceita_dados_completos(self):
        req = CriarUsuarioRequest(
            email="a@b.com", name="Test", password="Abc123!@", role="admin"
        )
        assert req.name == "Test"
        assert req.role == "admin"

    def test_role_default_viewer(self):
        req = CriarUsuarioRequest(
            email="a@b.com", name="Test", password="Abc123!@"
        )
        assert req.role == "viewer"

    def test_rejeita_senha_curta(self):
        with pytest.raises(ValidationError, match="8 caracteres"):
            CriarUsuarioRequest(
                email="a@b.com", name="T", password="Ab1!", role="viewer"
            )

    def test_rejeita_senha_sem_maiuscula(self):
        with pytest.raises(ValidationError, match="maiuscula"):
            CriarUsuarioRequest(
                email="a@b.com", name="T", password="abc12345!", role="viewer"
            )

    def test_rejeita_senha_sem_numero(self):
        with pytest.raises(ValidationError, match="numero"):
            CriarUsuarioRequest(
                email="a@b.com", name="T", password="Abcdefgh!", role="viewer"
            )

    def test_rejeita_senha_sem_especial(self):
        with pytest.raises(ValidationError, match="especial"):
            CriarUsuarioRequest(
                email="a@b.com", name="T", password="Abcdefg1", role="viewer"
            )

    def test_rejeita_role_invalido(self):
        with pytest.raises(ValidationError, match="Role invalido"):
            CriarUsuarioRequest(
                email="a@b.com", name="T", password="Abc123!@", role="hacker"
            )

    @pytest.mark.parametrize("role", ["admin", "copywriter", "designer", "reviewer", "viewer"])
    def test_aceita_todos_roles_validos(self, role):
        req = CriarUsuarioRequest(
            email="a@b.com", name="T", password="Abc123!@", role=role
        )
        assert req.role == role


# ===================================================================
# ConvidarUsuarioRequest
# ===================================================================
class TestConvidarUsuarioRequest:
    def test_cria_convite_valido(self):
        req = ConvidarUsuarioRequest(email="a@b.com", name="Test", role="designer")
        assert req.role == "designer"

    def test_rejeita_role_invalido(self):
        with pytest.raises(ValidationError, match="Role invalido"):
            ConvidarUsuarioRequest(email="a@b.com", name="T", role="superuser")


# ===================================================================
# AceitarConviteRequest — RN-021
# ===================================================================
class TestAceitarConviteRequest:
    def test_aceita_dados_validos(self):
        req = AceitarConviteRequest(token="abc123", password="Abc123!@")
        assert req.token == "abc123"

    def test_rejeita_senha_fraca(self):
        with pytest.raises(ValidationError):
            AceitarConviteRequest(token="abc123", password="fraca")


# ===================================================================
# AtualizarUsuarioRequest
# ===================================================================
class TestAtualizarUsuarioRequest:
    def test_todos_campos_opcionais(self):
        req = AtualizarUsuarioRequest()
        assert req.name is None
        assert req.role is None
        assert req.avatar_url is None

    def test_partial_update(self):
        req = AtualizarUsuarioRequest(name="Novo Nome")
        assert req.name == "Novo Nome"
        assert req.role is None

    def test_rejeita_role_invalido(self):
        with pytest.raises(ValidationError, match="Role invalido"):
            AtualizarUsuarioRequest(role="hacker")

    def test_aceita_role_none(self):
        req = AtualizarUsuarioRequest(role=None)
        assert req.role is None


# ===================================================================
# Responses — construcao correta
# ===================================================================
class TestLoginResponse:
    def test_cria_com_campos(self):
        resp = LoginResponse(
            access_token="tok",
            user_id="u1",
            tenant_id="t1",
            role="admin",
            name="A",
            email="a@b.c",
        )
        assert resp.token_type == "bearer"
        assert resp.access_token == "tok"


class TestUsuarioResponse:
    def test_cria_com_campos(self):
        from datetime import datetime, timezone

        resp = UsuarioResponse(
            user_id="u1",
            tenant_id="t1",
            email="a@b.c",
            name="A",
            role="admin",
            created_at=datetime.now(timezone.utc),
        )
        assert resp.avatar_url is None


class TestMeResponse:
    def test_cria_com_campos_minimos(self):
        resp = MeResponse(
            user_id="u1", tenant_id="t1", role="admin", email="a@b.c", name="A"
        )
        assert resp.created_at is None
        assert resp.avatar_url is None


class TestListarUsuariosResponse:
    def test_cria_lista_vazia(self):
        resp = ListarUsuariosResponse(usuarios=[], total=0)
        assert resp.total == 0
        assert resp.usuarios == []


class TestConviteResponse:
    def test_cria_com_campos(self):
        from datetime import datetime, timezone

        resp = ConviteResponse(
            invite_token="tok",
            email="a@b.c",
            name="A",
            role="designer",
            expires_at=datetime.now(timezone.utc),
            invite_url="http://x/aceitar?token=tok",
        )
        assert resp.invite_token == "tok"
