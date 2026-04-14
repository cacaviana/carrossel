"""Testes unitarios para rotas /api/test-slides no config router.

Testa:
- GET /api/test-slides retorna HTML quando pasta existe
- GET /api/test-slides retorna 404 quando pasta nao existe
- GET /api/test-slides/{filename} serve arquivo PNG
- GET /api/test-slides/{filename} retorna 404 para arquivo inexistente
- GET /api/test-slides/{filename} rejeita extensoes nao permitidas
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient


@pytest.fixture
def app():
    """Cria app FastAPI minima com o router de config."""
    from fastapi import FastAPI
    from routers.config import router
    app = FastAPI()
    app.include_router(router, prefix="/api")
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


class TestTestSlidesGallery:
    def test_gallery_retorna_html_com_pasta(self, client, tmp_path):
        # Criar PNGs fake
        (tmp_path / "slide-01.png").write_bytes(b"fake png")
        (tmp_path / "slide-02.png").write_bytes(b"fake png 2")

        with patch("routers.config._TEST_SLIDES_DIR", tmp_path):
            resp = client.get("/api/test-slides")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "slide-01" in resp.text
        assert "slide-02" in resp.text
        assert "Test Slides" in resp.text

    def test_gallery_404_sem_pasta(self, client):
        fake_dir = Path("C:/nao_existe_de_jeito_nenhum_xyz")
        with patch("routers.config._TEST_SLIDES_DIR", fake_dir):
            resp = client.get("/api/test-slides")
        assert resp.status_code == 404

    def test_gallery_html_contem_grid(self, client, tmp_path):
        (tmp_path / "test.png").write_bytes(b"png")
        with patch("routers.config._TEST_SLIDES_DIR", tmp_path):
            resp = client.get("/api/test-slides")
        assert "grid" in resp.text


class TestTestSlidesFile:
    def test_serve_png_existente(self, client, tmp_path):
        png_file = tmp_path / "slide-01.png"
        # Criar PNG minimo valido
        from PIL import Image
        from io import BytesIO
        img = Image.new("RGB", (10, 10))
        buf = BytesIO()
        img.save(buf, "PNG")
        png_file.write_bytes(buf.getvalue())

        with patch("routers.config._TEST_SLIDES_DIR", tmp_path):
            resp = client.get("/api/test-slides/slide-01.png")
        assert resp.status_code == 200

    def test_404_arquivo_inexistente(self, client, tmp_path):
        with patch("routers.config._TEST_SLIDES_DIR", tmp_path):
            resp = client.get("/api/test-slides/nao-existe.png")
        assert resp.status_code == 404

    def test_rejeita_extensao_invalida(self, client, tmp_path):
        # Criar arquivo .txt
        (tmp_path / "script.py").write_text("malicious")
        with patch("routers.config._TEST_SLIDES_DIR", tmp_path):
            resp = client.get("/api/test-slides/script.py")
        assert resp.status_code == 404

    def test_aceita_jpg(self, client, tmp_path):
        jpg_file = tmp_path / "photo.jpg"
        from PIL import Image
        from io import BytesIO
        img = Image.new("RGB", (10, 10))
        buf = BytesIO()
        img.save(buf, "JPEG")
        jpg_file.write_bytes(buf.getvalue())

        with patch("routers.config._TEST_SLIDES_DIR", tmp_path):
            resp = client.get("/api/test-slides/photo.jpg")
        assert resp.status_code == 200

    def test_aceita_webp(self, client, tmp_path):
        webp_file = tmp_path / "image.webp"
        from PIL import Image
        from io import BytesIO
        img = Image.new("RGB", (10, 10))
        buf = BytesIO()
        img.save(buf, "WEBP")
        webp_file.write_bytes(buf.getvalue())

        with patch("routers.config._TEST_SLIDES_DIR", tmp_path):
            resp = client.get("/api/test-slides/image.webp")
        assert resp.status_code == 200
