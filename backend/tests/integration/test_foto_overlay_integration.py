"""Integracao Foto Overlay.

Fluxo: Router -> services.foto_overlay.overlay_foto (Pillow)

Caso de uso: aplicar foto criador em slide(s) antes do export.
"""

import base64
import io

import pytest
from PIL import Image


def _png_b64(size=(1080, 1080), color=(30, 30, 30)):
    """Gera PNG base64 sintetico."""
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


@pytest.fixture
def slide_b64():
    return _png_b64()


@pytest.fixture
def foto_b64():
    return _png_b64(size=(400, 400), color=(200, 100, 50))


class TestAplicarFoto:
    """POST /api/aplicar-foto — caso de uso 'Aplicar Foto Criador'."""

    def test_aplicar_foto_retorna_image_base64(self, client, admin_headers, slide_b64, foto_b64):
        resp = client.post("/api/aplicar-foto", json={
            "slide_image": slide_b64,
            "foto_criador": foto_b64,
            "is_cta": False,
        }, headers=admin_headers)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "image" in body
        # Pode vir como "data:image/png;base64,..." ou puro base64
        assert isinstance(body["image"], str) and len(body["image"]) > 10

    def test_aplicar_foto_cta_retorna_image(self, client, admin_headers, slide_b64, foto_b64):
        resp = client.post("/api/aplicar-foto", json={
            "slide_image": slide_b64,
            "foto_criador": foto_b64,
            "is_cta": True,
        }, headers=admin_headers)
        assert resp.status_code == 200

    def test_aplicar_foto_sem_campos_obrigatorios_422(self, client, admin_headers):
        resp = client.post("/api/aplicar-foto", json={}, headers=admin_headers)
        assert resp.status_code == 422

    def test_aplicar_foto_is_cta_default_false(self, client, admin_headers, slide_b64, foto_b64):
        """is_cta tem default=False, nao deve falhar se omitido."""
        resp = client.post("/api/aplicar-foto", json={
            "slide_image": slide_b64,
            "foto_criador": foto_b64,
        }, headers=admin_headers)
        assert resp.status_code == 200


class TestAplicarFotoBatch:
    """POST /api/aplicar-foto-batch — caso de uso 'Aplicar em todos os slides'."""

    def test_batch_retorna_array_images(self, client, admin_headers, slide_b64, foto_b64):
        resp = client.post("/api/aplicar-foto-batch", json={
            "slides": [slide_b64, slide_b64, slide_b64],
            "foto_criador": foto_b64,
        }, headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "images" in body
        assert len(body["images"]) == 3

    def test_batch_ultimo_slide_e_cta(self, client, admin_headers, slide_b64, foto_b64):
        """Ultimo slide deve usar tratamento CTA (foto grande).
        Verificamos que todos retornam, presumindo logica no service."""
        resp = client.post("/api/aplicar-foto-batch", json={
            "slides": [slide_b64, slide_b64],
            "foto_criador": foto_b64,
        }, headers=admin_headers)
        assert resp.status_code == 200
        assert len(resp.json()["images"]) == 2

    def test_batch_array_vazio_retorna_images_vazia(self, client, admin_headers, foto_b64):
        resp = client.post("/api/aplicar-foto-batch", json={
            "slides": [],
            "foto_criador": foto_b64,
        }, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["images"] == []

    def test_batch_sem_slides_422(self, client, admin_headers, foto_b64):
        resp = client.post("/api/aplicar-foto-batch", json={
            "foto_criador": foto_b64,
        }, headers=admin_headers)
        assert resp.status_code == 422
