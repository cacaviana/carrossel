"""Integracao Validar ApiKey.

Caso de uso: POST /api/config/validar  (ClickUp 86e0y9age)

Criterios de aceite:
- Request de teste ao provider (Claude: messages create max_tokens=1; Gemini: similar)
- Retorna OK ou mensagem de erro clara (chave_invalida, quota_excedida, etc)
- Nao consome mais que 1-2 tokens
"""

import pytest


def _fake_resp(status_code=200, text="{}"):
    class R:
        def __init__(self, code, txt):
            self.status_code = code
            self.text = txt
        def json(self):
            import json
            return json.loads(self.text) if self.text else {}
    return R(status_code, text)


@pytest.fixture
def mock_httpx(monkeypatch):
    """Substitui httpx.AsyncClient dentro do api_key_validator_service."""
    import services.api_key_validator_service as svc

    state = {"last_url": None, "last_headers": None, "last_body": None, "resp_status": 200, "resp_text": "ok"}

    class _MockClient:
        def __init__(self, *a, **kw):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *a):
            pass
        async def post(self, url, headers=None, json=None):
            state["last_url"] = url
            state["last_headers"] = headers
            state["last_body"] = json
            return _fake_resp(state["resp_status"], state["resp_text"])
        async def get(self, url, headers=None):
            state["last_url"] = url
            state["last_headers"] = headers
            return _fake_resp(state["resp_status"], state["resp_text"])

    import httpx
    monkeypatch.setattr(svc, "httpx", type("M", (), {"AsyncClient": _MockClient, "TimeoutException": httpx.TimeoutException}))
    return state


class TestValidarApiKey:

    def test_payload_invalido_sem_provider_retorna_422(self, client, admin_headers):
        resp = client.post("/api/config/validar", headers=admin_headers, json={"api_key": "x"})
        assert resp.status_code == 422

    def test_provider_invalido_retorna_422(self, client, admin_headers):
        resp = client.post("/api/config/validar", headers=admin_headers,
                           json={"provider": "bard", "api_key": "x"})
        assert resp.status_code == 422

    def test_api_key_vazia_retorna_422(self, client, admin_headers):
        """min_length=1 no DTO impede string vazia."""
        resp = client.post("/api/config/validar", headers=admin_headers,
                           json={"provider": "claude", "api_key": ""})
        assert resp.status_code == 422

    def test_claude_200_retorna_ok(self, client, admin_headers, mock_httpx):
        mock_httpx["resp_status"] = 200
        mock_httpx["resp_text"] = '{"id":"msg_1"}'
        resp = client.post("/api/config/validar", headers=admin_headers,
                           json={"provider": "claude", "api_key": "sk-ant-fake"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["provider"] == "claude"
        # Confirma que foi chamado com max_tokens=1 (nao gastar tokens)
        assert mock_httpx["last_body"]["max_tokens"] == 1
        assert mock_httpx["last_headers"]["x-api-key"] == "sk-ant-fake"

    def test_claude_401_retorna_chave_invalida(self, client, admin_headers, mock_httpx):
        mock_httpx["resp_status"] = 401
        mock_httpx["resp_text"] = '{"error":"invalid_api_key"}'
        resp = client.post("/api/config/validar", headers=admin_headers,
                           json={"provider": "claude", "api_key": "sk-wrong"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is False
        assert body["erro"] == "chave_invalida"

    def test_claude_429_retorna_quota_excedida(self, client, admin_headers, mock_httpx):
        mock_httpx["resp_status"] = 429
        mock_httpx["resp_text"] = '{"error":"rate_limited"}'
        resp = client.post("/api/config/validar", headers=admin_headers,
                           json={"provider": "claude", "api_key": "sk-ok"})
        body = resp.json()
        assert body["ok"] is False
        assert body["erro"] == "quota_excedida"

    def test_gemini_usa_query_param_key(self, client, admin_headers, mock_httpx):
        mock_httpx["resp_status"] = 200
        mock_httpx["resp_text"] = '{"models":[]}'
        resp = client.post("/api/config/validar", headers=admin_headers,
                           json={"provider": "gemini", "api_key": "AIza-fake"})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        # Gemini passa key como query string
        assert "key=AIza-fake" in mock_httpx["last_url"]

    def test_openai_usa_bearer(self, client, admin_headers, mock_httpx):
        mock_httpx["resp_status"] = 200
        mock_httpx["resp_text"] = '{"data":[]}'
        resp = client.post("/api/config/validar", headers=admin_headers,
                           json={"provider": "openai", "api_key": "sk-openai"})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        assert mock_httpx["last_headers"]["Authorization"] == "Bearer sk-openai"

    def test_drive_json_invalido_retorna_json_invalido(self, client, admin_headers):
        resp = client.post("/api/config/validar", headers=admin_headers,
                           json={"provider": "drive", "api_key": "nao-eh-json"})
        body = resp.json()
        assert body["ok"] is False
        assert body["erro"] == "json_invalido"

    def test_drive_json_valido_sem_campos_obrigatorios(self, client, admin_headers):
        import json
        resp = client.post("/api/config/validar", headers=admin_headers,
                           json={"provider": "drive", "api_key": json.dumps({"type": "service_account"})})
        body = resp.json()
        assert body["ok"] is False
        assert body["erro"] == "campos_faltando"

    def test_timeout_retorna_erro_timeout(self, client, admin_headers, monkeypatch):
        """Timeout na chamada externa vira erro 'timeout'."""
        import services.api_key_validator_service as svc
        import httpx

        class _TimeoutClient:
            def __init__(self, *a, **kw): pass
            async def __aenter__(self): return self
            async def __aexit__(self, *a): pass
            async def post(self, *a, **kw): raise httpx.TimeoutException("timeout")
            async def get(self, *a, **kw): raise httpx.TimeoutException("timeout")

        monkeypatch.setattr(svc, "httpx", type("M", (), {
            "AsyncClient": _TimeoutClient,
            "TimeoutException": httpx.TimeoutException,
        }))

        resp = client.post("/api/config/validar", headers=admin_headers,
                           json={"provider": "claude", "api_key": "sk-x"})
        body = resp.json()
        assert body["ok"] is False
        assert body["erro"] == "timeout"

    def test_sem_auth_bloqueia(self, client):
        resp = client.post("/api/config/validar",
                           json={"provider": "claude", "api_key": "x"})
        assert resp.status_code in (401, 403)


class TestContrato:
    def test_rota_registrada(self, client):
        paths = client.get("/openapi.json").json()["paths"]
        assert "/api/config/validar" in paths
        assert "post" in paths["/api/config/validar"]
