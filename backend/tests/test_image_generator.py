"""Testa logica do image_generator (model selection, variações, retry)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.image_generator import _select_model, FALLBACK_MODEL
from skills.variation_engine import gerar_variacoes


def test_select_model_capa_usa_pro():
    model = _select_model(slide_index=1, total_slides=10)
    assert "pro" in model.lower()


def test_select_model_cta_usa_pro():
    model = _select_model(slide_index=10, total_slides=10)
    assert "pro" in model.lower()


def test_select_model_intermediario_usa_pro():
    """Todos os slides usam Pro para qualidade consistente."""
    for i in range(2, 10):
        model = _select_model(slide_index=i, total_slides=10)
        assert "pro" in model.lower(), f"Slide {i} deveria usar Pro, mas usa {model}"


def test_select_model_3_slides():
    """3 slides: todos Pro."""
    assert "pro" in _select_model(1, 3).lower()
    assert "pro" in _select_model(2, 3).lower()
    assert "pro" in _select_model(3, 3).lower()


def test_select_model_7_slides_todos_pro():
    """7 slides: todos Pro para qualidade consistente."""
    pro_count = sum(1 for i in range(1, 8) if "pro" in _select_model(i, 7).lower())
    assert pro_count == 7, f"Esperado 7 Pro, mas tem {pro_count}"


def test_fallback_model_is_flash():
    assert "flash" in FALLBACK_MODEL.lower()


def test_gerar_variacoes_retorna_3():
    variacoes = gerar_variacoes("teste prompt")
    assert len(variacoes) == 3


def test_gerar_variacoes_primeira_e_original():
    prompt = "dark mode slide with purple gradient"
    variacoes = gerar_variacoes(prompt)
    assert variacoes[0] == prompt


def test_gerar_variacoes_segunda_e_minimalista():
    variacoes = gerar_variacoes("test")
    assert "minimalist" in variacoes[1].lower() or "Minimalist" in variacoes[1]


def test_gerar_variacoes_terceira_e_dramatica():
    variacoes = gerar_variacoes("test")
    assert "dramatic" in variacoes[2].lower() or "Dramatic" in variacoes[2]
