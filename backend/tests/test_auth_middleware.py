"""Testes unitarios — middleware/auth.py

Cobre: hash_password, verify_password, create_access_token,
       get_current_user, require_role, JWT 24h (RN-018).
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from jose import jwt

# ---------- importa o modulo sob teste ----------
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from middleware.auth import (
    JWT_ALGORITHM,
    JWT_EXPIRE_HOURS,
    JWT_SECRET_KEY,
    CurrentUser,
    create_access_token,
    get_current_user,
    hash_password,
    require_role,
    verify_password,
)
from fastapi import HTTPException


# ===================================================================
# hash_password / verify_password
# ===================================================================
class TestPasswordHashing:
    def test_hash_retorna_string_diferente_da_senha(self):
        hashed = hash_password("Abc123!@")
        assert hashed != "Abc123!@"
        assert len(hashed) > 20

    def test_verify_aceita_senha_correta(self):
        hashed = hash_password("Abc123!@")
        assert verify_password("Abc123!@", hashed) is True

    def test_verify_rejeita_senha_errada(self):
        hashed = hash_password("Abc123!@")
        assert verify_password("SenhaErrada1!", hashed) is False

    def test_hashes_diferentes_para_mesma_senha(self):
        h1 = hash_password("Abc123!@")
        h2 = hash_password("Abc123!@")
        assert h1 != h2  # salt diferente


# ===================================================================
# create_access_token
# ===================================================================
class TestCreateAccessToken:
    def test_token_contem_payload(self):
        data = {"user_id": "u1", "tenant_id": "t1", "role": "admin", "email": "a@b.c"}
        token = create_access_token(data)
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        assert decoded["user_id"] == "u1"
        assert decoded["tenant_id"] == "t1"
        assert decoded["role"] == "admin"
        assert decoded["email"] == "a@b.c"

    def test_token_expira_em_24h_por_padrao(self):
        """RN-018: JWT expira em 24h."""
        assert JWT_EXPIRE_HOURS == 24
        token = create_access_token({"sub": "test"})
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        exp = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = exp - now
        # deve estar entre 23h55 e 24h05
        assert timedelta(hours=23, minutes=55) < diff < timedelta(hours=24, minutes=5)

    def test_token_custom_expiry(self):
        token = create_access_token({"sub": "test"}, expires_delta=timedelta(minutes=5))
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        exp = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = exp - now
        assert diff < timedelta(minutes=6)

    def test_token_expirado_nao_decodifica(self):
        token = create_access_token({"sub": "test"}, expires_delta=timedelta(seconds=-1))
        with pytest.raises(Exception):
            jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


# ===================================================================
# get_current_user
# ===================================================================
class TestGetCurrentUser:
    def _make_credentials(self, token: str):
        cred = MagicMock()
        cred.credentials = token
        return cred

    def test_decodifica_token_valido(self):
        data = {
            "user_id": "u1",
            "tenant_id": "t1",
            "role": "admin",
            "email": "a@b.c",
            "name": "Admin",
        }
        token = create_access_token(data)
        user = get_current_user(self._make_credentials(token))
        assert isinstance(user, CurrentUser)
        assert user.user_id == "u1"
        assert user.tenant_id == "t1"
        assert user.role == "admin"
        assert user.email == "a@b.c"
        assert user.name == "Admin"

    def test_retorna_401_para_token_invalido(self):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(self._make_credentials("token.invalido.aqui"))
        assert exc_info.value.status_code == 401

    def test_retorna_401_quando_campos_faltam(self):
        # token sem user_id
        token = create_access_token({"tenant_id": "t1", "role": "admin", "email": "a@b.c"})
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(self._make_credentials(token))
        assert exc_info.value.status_code == 401

    def test_name_default_vazio_se_ausente(self):
        data = {"user_id": "u1", "tenant_id": "t1", "role": "admin", "email": "a@b.c"}
        token = create_access_token(data)
        user = get_current_user(self._make_credentials(token))
        assert user.name == ""


# ===================================================================
# require_role
# ===================================================================
class TestRequireRole:
    def _make_user(self, role: str) -> CurrentUser:
        return CurrentUser(
            user_id="u1", tenant_id="t1", role=role, email="a@b.c", name="Test"
        )

    def test_permite_role_autorizado(self):
        checker = require_role("admin", "copywriter")
        user = self._make_user("admin")
        result = checker(current_user=user)
        assert result.role == "admin"

    def test_bloqueia_role_nao_autorizado(self):
        checker = require_role("admin")
        user = self._make_user("viewer")
        with pytest.raises(HTTPException) as exc_info:
            checker(current_user=user)
        assert exc_info.value.status_code == 403
