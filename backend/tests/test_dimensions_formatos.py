"""Testes unitarios — utils/dimensions.py.

get_dims e a fonte unica de verdade para dimensoes dos 3 formatos +
carrossel. Usado por:
 - imagem_factory (aspect ratio do Gemini)
 - smart_image_service (escala do Pillow overlay)
 - pdf_service (tamanho da pagina)
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.dimensions import get_dims, get_prompt_size_str, get_page_mm, FORMATS


class TestGetDims:
    def test_carrossel_portrait_4_5(self):
        d = get_dims("carrossel")
        assert d["width"] == 1080
        assert d["height"] == 1350
        assert d["ratio"] == "4:5"

    def test_post_unico_quadrado_1_1(self):
        d = get_dims("post_unico")
        assert d["width"] == d["height"] == 1080
        assert d["ratio"] == "1:1"

    def test_thumbnail_youtube_landscape_16_9(self):
        d = get_dims("thumbnail_youtube")
        assert d["width"] == 1280
        assert d["height"] == 720
        assert d["ratio"] == "16:9"

    def test_capa_reels_tall_9_16(self):
        d = get_dims("capa_reels")
        assert d["width"] == 1080
        assert d["height"] == 1920
        assert d["ratio"] == "9:16"

    def test_formato_invalido_cai_no_fallback_carrossel(self):
        """FORMATS.get(formato, FORMATS['carrossel']) — fallback duro."""
        # Desabilitar mongo/json para forcar fallback hardcoded
        with patch("utils.dimensions._carregar_dims_mongo", return_value=None), \
             patch("utils.dimensions._carregar_dims_json", return_value=None):
            d = get_dims("formato_que_nao_existe")
        assert d == FORMATS["carrossel"]

    def test_dims_incluem_campos_obrigatorios(self):
        d = get_dims("carrossel")
        for campo in ("width", "height", "ratio", "label"):
            assert campo in d


class TestGetPromptSizeStr:
    @pytest.mark.parametrize("formato,expected_size", [
        ("carrossel", "1080x1350px, 4:5 portrait"),
        ("post_unico", "1080x1080px, 1:1 square"),
        ("thumbnail_youtube", "1280x720px, 16:9 landscape"),
        ("capa_reels", "1080x1920px, 9:16 tall portrait"),
    ])
    def test_string_pro_prompt(self, formato, expected_size):
        with patch("utils.dimensions._carregar_dims_mongo", return_value=None), \
             patch("utils.dimensions._carregar_dims_json", return_value=None):
            s = get_prompt_size_str(formato)
        assert s == expected_size


class TestGetPageMm:
    """PDF: 1px = 0.2mm a 127 DPI."""

    @pytest.mark.parametrize("formato", ["post_unico", "capa_reels", "thumbnail_youtube", "carrossel"])
    def test_retorna_tuple_w_h(self, formato):
        with patch("utils.dimensions._carregar_dims_mongo", return_value=None), \
             patch("utils.dimensions._carregar_dims_json", return_value=None):
            w, h = get_page_mm(formato)
        assert isinstance(w, float)
        assert isinstance(h, float)
        assert w > 0 and h > 0

    def test_page_mm_respeita_aspecto(self):
        """Carrossel: ratio 4:5 = width/height = 0.8."""
        with patch("utils.dimensions._carregar_dims_mongo", return_value=None), \
             patch("utils.dimensions._carregar_dims_json", return_value=None):
            w, h = get_page_mm("carrossel")
        assert abs((w / h) - (1080 / 1350)) < 0.01


# =============================================================================
# Parametrizacao: get_dims funciona pros 3 formatos novos
# =============================================================================
@pytest.mark.parametrize("formato,esperado_w,esperado_h,esperado_ratio", [
    ("post_unico", 1080, 1080, "1:1"),
    ("capa_reels", 1080, 1920, "9:16"),
    ("thumbnail_youtube", 1280, 720, "16:9"),
])
class TestGetDimsPorFormato:
    def test_dims_corretos_por_formato(self, formato, esperado_w, esperado_h, esperado_ratio):
        with patch("utils.dimensions._carregar_dims_mongo", return_value=None):
            # JSON pode dar os mesmos valores — nao precisa mockar
            d = get_dims(formato)
        assert d["width"] == esperado_w
        assert d["height"] == esperado_h
        assert d["ratio"] == esperado_ratio

    def test_prompt_size_str_por_formato(self, formato, esperado_w, esperado_h, esperado_ratio):
        with patch("utils.dimensions._carregar_dims_mongo", return_value=None):
            s = get_prompt_size_str(formato)
        assert f"{esperado_w}x{esperado_h}" in s
        assert esperado_ratio in s
