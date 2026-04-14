"""Testes unitarios para inferir_tipo_layout em factories/pipeline_factory.py

Testa todas as regras de inferencia:
- cover/cta/code -> texto
- left/right labels -> comparativo
- bullets com numeros/porcentagens -> dados
- bullets sem numeros -> lista
- fallback -> texto
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from factories.pipeline_factory import inferir_tipo_layout as _inferir_tipo_layout


class TestInferirTipoLayout:
    # --- Tipos diretos (cover, cta, code) -> texto ---

    def test_cover_retorna_texto(self):
        assert _inferir_tipo_layout({"type": "cover"}) == "texto"

    def test_cta_retorna_texto(self):
        assert _inferir_tipo_layout({"type": "cta"}) == "texto"

    def test_code_retorna_texto(self):
        assert _inferir_tipo_layout({"type": "code"}) == "texto"

    # --- Comparativo ---

    def test_left_label_retorna_comparativo(self):
        slide = {"type": "content", "left_label": "Python", "right_label": "JavaScript"}
        assert _inferir_tipo_layout(slide) == "comparativo"

    def test_left_items_retorna_comparativo(self):
        slide = {"type": "content", "left_items": ["a", "b"]}
        assert _inferir_tipo_layout(slide) == "comparativo"

    # --- Dados (bullets com numeros) ---

    def test_bullets_com_numeros_retorna_dados(self):
        slide = {"type": "content", "bullets": ["90% das empresas", "2x mais rapido", "500 usuarios"]}
        assert _inferir_tipo_layout(slide) == "dados"

    def test_bullets_com_porcentagem_retorna_dados(self):
        slide = {"type": "content", "bullets": ["Performance 95%", "Uptime 99.9%"]}
        assert _inferir_tipo_layout(slide) == "dados"

    # --- Lista (bullets sem numeros dominantes) ---

    def test_bullets_texto_retorna_lista(self):
        slide = {"type": "content", "bullets": ["Modularidade", "Reutilizacao", "Testabilidade"]}
        assert _inferir_tipo_layout(slide) == "lista"

    def test_bullets_mistos_pouco_numero_retorna_lista(self):
        """Menos de 50% com numeros = lista, nao dados."""
        slide = {"type": "content", "bullets": ["Python e bom", "100 vezes melhor", "Aprenda agora", "Use sempre"]}
        # 1 de 4 = 25% < 50% -> lista
        assert _inferir_tipo_layout(slide) == "lista"

    # --- Fallback -> texto ---

    def test_sem_type_retorna_texto_ou_lista(self):
        """Sem type e sem bullets, retorna texto."""
        slide = {}
        assert _inferir_tipo_layout(slide) == "texto"

    def test_content_sem_bullets_retorna_texto(self):
        slide = {"type": "content"}
        assert _inferir_tipo_layout(slide) == "texto"

    def test_bullets_vazio_retorna_texto(self):
        slide = {"type": "content", "bullets": []}
        assert _inferir_tipo_layout(slide) == "texto"

    # --- Edge cases ---

    def test_cover_com_bullets_ignora_bullets(self):
        """Cover sempre retorna texto, independente de bullets."""
        slide = {"type": "cover", "bullets": ["90% mais rapido"]}
        assert _inferir_tipo_layout(slide) == "texto"

    def test_threshold_exato_50_porcento(self):
        """Exatamente 50% com numeros -> dados."""
        slide = {"type": "content", "bullets": ["90% uptime", "e leve"]}
        assert _inferir_tipo_layout(slide) == "dados"
