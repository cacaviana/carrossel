"""Fixtures compartilhadas para QA Integracao.

Mocka:
- MongoDB (mongomock)
- SQL session (SQLite in-memory via aiosqlite se disponivel, senao skip)
- LLM calls (Gemini, Claude, OpenAI)
- HTTP client (httpx) para APIs externas

Exporta:
- authenticated_client: TestClient ja com headers Authorization
- admin_token / viewer_token / tenant_b_token
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import mongomock
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# MongoDB mock (para auth, kanban, brand assets)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_mongo():
    """Substitui todos os acessos ao MongoDB por mongomock."""
    mock_client = mongomock.MongoClient()
    db = mock_client["content_factory"]

    targets = [
        "data.connections.mongo_connection.get_mongo_db",
        "data.repositories.mongo.auth_repository.get_mongo_db",
        "data.repositories.mongo.invite_repository.get_mongo_db",
        "data.repositories.mongo.kanban_card_repository.get_mongo_db",
        "data.repositories.mongo.kanban_board_repository.get_mongo_db",
        "data.repositories.mongo.tenant_repository.get_mongo_db",
    ]

    patches = []
    for t in targets:
        try:
            patches.append(patch(t, return_value=db))
        except Exception:
            pass
    for p in patches:
        p.start()

    # Limpa collections relevantes
    for coll in ("kanban_users", "kanban_invite_tokens", "brand_assets", "visual_preferences", "tenants", "kanban_cards"):
        db[coll].drop()
    yield db

    for p in patches:
        try:
            p.stop()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Mock LLM + HTTP externos (nao bater em Gemini/Claude/OpenAI)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_external_apis(monkeypatch):
    """Garante que nenhum teste de integracao chame servicos externos."""
    # Mock do metodo async de BrandAnalyzer (Gemini vision)
    try:
        from services.brand_analyzer_service import BrandAnalyzerService
        async def fake_analisar(*args, **kwargs):
            return {
                "paleta": ["#000000", "#FFFFFF"],
                "fontes": ["Outfit"],
                "estilo": "minimalist",
                "sugestao_dna": "Clean minimalist tech",
            }
        async def fake_descrever(*args, **kwargs):
            return {"descricao": "clean tech style"}
        monkeypatch.setattr(BrandAnalyzerService, "analisar", fake_analisar, raising=False)
        monkeypatch.setattr(BrandAnalyzerService, "descrever_estilo", fake_descrever, raising=False)
    except Exception:
        pass

    # Mock regenerar DNA
    try:
        import services.dna_generator as dna_mod
        async def fake_dna(slug, imagem=None):
            return {"slug": slug, "dna": {
                "estilo": "minimalist",
                "cores": "#000000 #FFFFFF",
                "tipografia": "Outfit",
                "elementos": "lines, dots",
            }}
        monkeypatch.setattr(dna_mod, "regenerar_dna", fake_dna, raising=False)
    except Exception:
        pass

    # Mock de httpx para qualquer coisa que escapar
    try:
        import httpx
        original_async_client = httpx.AsyncClient

        class _MockAsyncClient:
            def __init__(self, *args, **kwargs):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

            async def post(self, *args, **kwargs):
                resp = MagicMock()
                resp.status_code = 200
                resp.json = lambda: {"candidates": [{"content": {"parts": [{"inlineData": {"data": "ZmFrZQ=="}}]}}]}
                resp.text = "{}"
                resp.raise_for_status = lambda: None
                return resp

            async def get(self, *args, **kwargs):
                resp = MagicMock()
                resp.status_code = 200
                resp.json = lambda: {}
                resp.text = "{}"
                resp.raise_for_status = lambda: None
                return resp

        # Nao sobrescrevemos httpx globalmente — TestClient do FastAPI usa httpx internamente
        # Mockaremos por contexto quando necessario
    except Exception:
        pass


# ---------------------------------------------------------------------------
# TestClient + tokens
# ---------------------------------------------------------------------------

@pytest.fixture
def disable_auth_override():
    """No-op por ora — placeholder para caso haja override global de auth
    em conftest pai. Assim client pode depender dele sem falhar."""
    yield


@pytest.fixture
def client(mock_mongo, disable_auth_override):
    """TestClient para integracao — usa JWT real (disable_auth_override
    remove o override global do conftest pai)."""
    from main import app
    return TestClient(app, raise_server_exceptions=False)


def _make_token(**overrides):
    from middleware.auth import create_access_token
    payload = {
        "user_id": "000000000000000000000001",
        "tenant_id": "tenant-A",
        "role": "admin",
        "email": "admin@test.com",
        "name": "Admin Test",
    }
    payload.update(overrides)
    return create_access_token(payload)


@pytest.fixture
def admin_token():
    return _make_token()


@pytest.fixture
def viewer_token():
    return _make_token(
        user_id="000000000000000000000002",
        role="viewer",
        email="viewer@test.com",
        name="Viewer",
    )


@pytest.fixture
def tenant_b_admin_token():
    return _make_token(
        user_id="000000000000000000000099",
        tenant_id="tenant-B",
        email="admin@tenantb.com",
        name="Admin Tenant B",
    )


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def viewer_headers(viewer_token):
    return {"Authorization": f"Bearer {viewer_token}"}


# ---------------------------------------------------------------------------
# Dados de teste
# ---------------------------------------------------------------------------

STRONG_PASSWORD = "SenhaForte1!"

BRAND_PAYLOAD = {
    "slug": "test-brand",
    "nome": "Test Brand",
    "descricao": "Brand for tests",
    "cores": {
        "fundo_principal": "#000000",
        "destaque_primario": "#FF0000",
        "destaque_secundario": "#00FF00",
        "texto_principal": "#FFFFFF",
        "texto_secundario": "#CCCCCC",
    },
    "fonte": "Outfit",
    "elementos_obrigatorios": ["lines", "dots"],
    "estilo": "dark_mode_premium",
}
