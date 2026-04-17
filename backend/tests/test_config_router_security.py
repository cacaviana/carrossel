"""Testes de seguranca para rotas test-slides.

Verifica que path traversal nao funciona.
"""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from fastapi import FastAPI
from routers.config import router


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router, prefix="/api")
    # JWT e obrigatorio em prod — tests instalam override para simular usuario autenticado
    from tests.conftest import install_auth_override_on_app
    install_auth_override_on_app(app)
    return TestClient(app)


class TestTestSlidesSeguranca:
    def test_path_traversal_bloqueado(self, client, tmp_path):
        """Tenta acessar arquivo fora de test_slides via ../"""
        # Criar arquivo secreto fora de test_slides
        secret = tmp_path / "secret.png"
        secret.write_bytes(b"secret data")

        test_slides = tmp_path / "test_slides"
        test_slides.mkdir()

        with patch("routers.config._TEST_SLIDES_DIR", test_slides):
            # Tentar path traversal
            resp = client.get("/api/test-slides/..%2Fsecret.png")
        # Deve retornar 404 (nao existe dentro de test_slides)
        assert resp.status_code in (404, 400, 422)

    def test_filename_sem_extensao_bloqueado(self, client, tmp_path):
        (tmp_path / "noext").write_bytes(b"data")
        with patch("routers.config._TEST_SLIDES_DIR", tmp_path):
            resp = client.get("/api/test-slides/noext")
        assert resp.status_code == 404
