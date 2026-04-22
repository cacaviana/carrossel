"""Bug: avatar_fixer tinha aspectRatio hardcoded em '4:5', convertendo thumb 16:9
em 4:5 na passagem do Pass 2. Fix: respeitar o formato pra preservar aspect ratio.
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from services.avatar_fixer import corrigir_avatar


class _FakeResp:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = "ok"
    def json(self): return self._json
    def raise_for_status(self): pass


@pytest.fixture
def captured_payload():
    """Captura o payload enviado pro Gemini pra inspecionar."""
    return {}


@pytest.fixture
def mock_gemini(captured_payload, monkeypatch):
    """Intercepta httpx pra capturar payload + devolver imagem fake."""
    import services.avatar_fixer as svc

    fake_response = {
        "candidates": [{
            "content": {"parts": [{"inlineData": {"data": "ZmFrZV9nZW5lcmF0ZWRfaW1nX2I2NA=="}}]}
        }]
    }

    class _MockClient:
        def __init__(self, *a, **kw): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        async def post(self, url, json=None, headers=None):
            captured_payload["url"] = url
            captured_payload["body"] = json
            return _FakeResp(200, fake_response)

    import httpx
    monkeypatch.setattr(svc, "httpx", type("M", (), {"AsyncClient": _MockClient}))
    # Mock _load_avatars
    monkeypatch.setattr(svc, "_load_avatars", lambda s: ["AV1_B64", "AV2_B64", "AV3_B64"])
    return captured_payload


class TestAspectRatioPreservado:

    def test_thumbnail_usa_16x9(self, mock_gemini):
        asyncio.run(corrigir_avatar("IMG_B64", "thumbs", "api-key", formato="thumbnail_youtube"))
        aspect = mock_gemini["body"]["generationConfig"]["imageConfig"]["aspectRatio"]
        assert aspect == "16:9"

    def test_carrossel_usa_4x5(self, mock_gemini):
        asyncio.run(corrigir_avatar("IMG_B64", "brand", "api-key", formato="carrossel"))
        aspect = mock_gemini["body"]["generationConfig"]["imageConfig"]["aspectRatio"]
        assert aspect == "4:5"

    def test_reels_usa_9x16(self, mock_gemini):
        asyncio.run(corrigir_avatar("IMG_B64", "brand", "api-key", formato="capa_reels"))
        aspect = mock_gemini["body"]["generationConfig"]["imageConfig"]["aspectRatio"]
        assert aspect == "9:16"

    def test_post_unico_usa_4x5(self, mock_gemini):
        """post_unico agora eh 4:5 (depois da migracao de 1:1)."""
        asyncio.run(corrigir_avatar("IMG_B64", "brand", "api-key", formato="post_unico"))
        aspect = mock_gemini["body"]["generationConfig"]["imageConfig"]["aspectRatio"]
        assert aspect == "4:5"

    def test_formato_default_e_carrossel(self, mock_gemini):
        """Sem passar formato, default eh carrossel (4:5)."""
        asyncio.run(corrigir_avatar("IMG_B64", "brand", "api-key"))
        aspect = mock_gemini["body"]["generationConfig"]["imageConfig"]["aspectRatio"]
        assert aspect == "4:5"
