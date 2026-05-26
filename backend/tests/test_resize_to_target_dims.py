"""Gemini gera em resolucao nativa (928x1152, 1024x1024, etc) que difere do target
(1080x1350 pra post_unico, 1080x1920 pra reels). Resize via PIL exporta no target.

Regras:
- Se ja bate o target, retorna como veio
- Se ratio bate (tolerancia 5%), faz upscale LANCZOS
- Se ratio nao bate, retorna original (nao distorce)
"""

import base64
import io

import pytest
from PIL import Image

from services.smart_image_service import _resize_to_target_dims


def _png_b64(w: int, h: int) -> str:
    img = Image.new("RGB", (w, h), (128, 64, 200))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _dims_of(b64: str) -> tuple[int, int]:
    raw = b64.split(",", 1)[1] if "," in b64 else b64
    return Image.open(io.BytesIO(base64.b64decode(raw))).size


def _target(w: int, h: int, ratio: str) -> dict:
    return {"width": w, "height": h, "ratio": ratio, "label": "x"}


class TestResizeToTargetDims:

    def test_ja_bate_target_retorna_mesma(self):
        b64 = _png_b64(1080, 1350)
        out = _resize_to_target_dims(b64, _target(1080, 1350, "4:5"))
        assert out == b64
        assert _dims_of(out) == (1080, 1350)

    def test_ratio_bate_mas_menor_upscale_pra_target(self):
        """Caso tipico: Gemini gera 928x1152 (4:5), target eh 1080x1350."""
        b64 = _png_b64(928, 1152)
        out = _resize_to_target_dims(b64, _target(1080, 1350, "4:5"))
        assert _dims_of(out) == (1080, 1350)

    def test_quadrado_1024_vira_1080(self):
        """Caso mencionado pelo designer: 1024x1024 deve virar 1080x1080 (quando target eh quadrado)."""
        b64 = _png_b64(1024, 1024)
        out = _resize_to_target_dims(b64, _target(1080, 1080, "1:1"))
        assert _dims_of(out) == (1080, 1080)

    def test_ratio_diferente_nao_redimensiona(self):
        """Nao distorce: se ratio nao bate, retorna original pra nao deformar."""
        b64 = _png_b64(1080, 1080)  # 1:1
        out = _resize_to_target_dims(b64, _target(1080, 1350, "4:5"))
        # Retornou o original — evita deformacao
        assert _dims_of(out) == (1080, 1080)

    def test_ratio_bate_com_pequena_diferenca_aceita(self):
        """1:1 tolerancia de 5% — 1000x1000 (diff ~0%) bate com 1080x1080."""
        b64 = _png_b64(1000, 1000)
        out = _resize_to_target_dims(b64, _target(1080, 1080, "1:1"))
        assert _dims_of(out) == (1080, 1080)

    def test_reels_1080x1920_upscale(self):
        """Gemini pode gerar 720x1280 (9:16), target eh 1080x1920."""
        b64 = _png_b64(720, 1280)
        out = _resize_to_target_dims(b64, _target(1080, 1920, "9:16"))
        assert _dims_of(out) == (1080, 1920)

    def test_thumbnail_1280x720_upscale(self):
        b64 = _png_b64(960, 540)  # 16:9 menor
        out = _resize_to_target_dims(b64, _target(1280, 720, "16:9"))
        assert _dims_of(out) == (1280, 720)

    def test_dims_sem_width_retorna_original(self):
        b64 = _png_b64(500, 500)
        out = _resize_to_target_dims(b64, {"ratio": "1:1"})
        assert out == b64

    def test_b64_com_data_uri_preserva_prefixo(self):
        b64_raw = _png_b64(928, 1152)
        data_uri = f"data:image/png;base64,{b64_raw}"
        out = _resize_to_target_dims(data_uri, _target(1080, 1350, "4:5"))
        assert out.startswith("data:image/png;base64,")
        assert _dims_of(out) == (1080, 1350)

    def test_b64_invalido_nao_quebra(self):
        out = _resize_to_target_dims("nao-eh-base64-valido", _target(1080, 1350, "4:5"))
        assert out == "nao-eh-base64-valido"
