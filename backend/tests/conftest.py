"""Fixtures compartilhadas para todos os testes backend.

O grande foco aqui: injetar um usuario de teste autenticado nos routers
que agora exigem JWT via `Depends(get_current_user)`.

Estrategia:
- `_auto_override_current_user` (autouse): instala override em `main.app`
  retornando um `CurrentUser` fake com tenant_id="itvalley" e role="admin"
  para TODOS os testes. Isso mantem testes legados funcionando sem mudanca.
- Testes que precisam validar o fluxo de auth real (ex: test_auth_integration.py)
  limpam o override manualmente via a fixture `disable_auth_override`.
- `authenticated_client`: TestClient do main.app ja com override instalado.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Garante que o backend/ esteja no sys.path antes de importar main/middleware
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from middleware.auth import CurrentUser, get_current_user


FAKE_TEST_USER = CurrentUser(
    user_id="000000000000000000000001",
    tenant_id="itvalley",
    role="admin",
    email="test@itvalley.com",
    name="Test User",
)


def _fake_get_current_user() -> CurrentUser:
    return FAKE_TEST_USER


@pytest.fixture(autouse=True)
def _auto_override_current_user(request):
    """Instala override de get_current_user no main.app para todos os testes.

    Testes que precisam validar JWT real (ex: test_auth_integration.py) usam
    a fixture `disable_auth_override` que remove este override antes de rodar.
    """
    # Se o teste solicita desativar o override (auth integration), nao instala
    if "disable_auth_override" in request.fixturenames:
        yield
        return

    from main import app as main_app

    main_app.dependency_overrides[get_current_user] = _fake_get_current_user
    yield
    main_app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def disable_auth_override():
    """Marca o teste para NAO receber o override automatico de get_current_user.

    Use em testes que validam o fluxo real de JWT (ex: tests de /api/auth/*).
    """
    from main import app as main_app

    main_app.dependency_overrides.pop(get_current_user, None)
    yield
    main_app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def authenticated_client():
    """TestClient do main.app com get_current_user ja sobrescrito.

    Retorna um `CurrentUser` fake com tenant_id="itvalley" e role="admin".
    Util para testes de routers protegidos por JWT.
    """
    from main import app as main_app

    main_app.dependency_overrides[get_current_user] = _fake_get_current_user
    client = TestClient(main_app, raise_server_exceptions=False)
    yield client
    main_app.dependency_overrides.pop(get_current_user, None)


def install_auth_override_on_app(app) -> None:
    """Helper para testes que criam FastAPI() proprio (nao usam main.app).

    Uso:
        app = FastAPI()
        app.include_router(router, prefix="/api")
        install_auth_override_on_app(app)
    """
    app.dependency_overrides[get_current_user] = _fake_get_current_user
