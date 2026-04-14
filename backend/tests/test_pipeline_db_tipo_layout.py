"""Testes unitarios para logica de propagacao de tipo_layout no pipeline_db_service.

Foco: Verificar que a funcao criar_pipeline monta o JSON de copywriter
com tipo_layout corretamente quando modo_entrada == 'texto_pronto'.

Como o service usa banco SQL, testamos a logica de montagem do JSON isoladamente,
sem depender do banco de dados.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestTipoLayoutPropagacao:
    """Testa a logica de montagem de slides que existe dentro de criar_pipeline."""

    def _montar_slides_para_copy(self, slides_texto_pronto):
        """Replica a logica de montagem de slides_para_copy do pipeline_db_service.criar_pipeline."""
        slides_para_copy = []
        for idx, s in enumerate(slides_texto_pronto):
            tipo = "capa" if idx == 0 else ("cta" if idx == len(slides_texto_pronto) - 1 else "conteudo")
            tipo_layout = (s.get("tipo_layout") if isinstance(s, dict) else getattr(s, "tipo_layout", None)) or None
            entry = {
                "indice": idx + 1,
                "tipo": tipo,
                "titulo": s.get("principal", "") if isinstance(s, dict) else s.principal,
                "corpo": s.get("alternativo", "") if isinstance(s, dict) else s.alternativo,
                "notas": "Texto fornecido pelo usuario -- NAO reescrever",
            }
            if tipo_layout:
                entry["tipo_layout"] = tipo_layout
            slides_para_copy.append(entry)
        return slides_para_copy

    def test_tipo_layout_propagado_em_slides(self):
        slides = [
            {"principal": "Capa", "alternativo": "", "tipo_layout": "texto"},
            {"principal": "Dados", "alternativo": "90% mais rapido", "tipo_layout": "dados"},
            {"principal": "CTA", "alternativo": "Siga", "tipo_layout": "texto"},
        ]
        result = self._montar_slides_para_copy(slides)
        assert result[0]["tipo_layout"] == "texto"
        assert result[1]["tipo_layout"] == "dados"
        assert result[2]["tipo_layout"] == "texto"

    def test_tipo_layout_none_nao_incluido(self):
        slides = [
            {"principal": "Capa", "alternativo": "", "tipo_layout": None},
            {"principal": "Body", "alternativo": "conteudo"},
        ]
        result = self._montar_slides_para_copy(slides)
        assert "tipo_layout" not in result[0]
        assert "tipo_layout" not in result[1]

    def test_tipo_layout_vazio_nao_incluido(self):
        slides = [
            {"principal": "Capa", "alternativo": "", "tipo_layout": ""},
        ]
        result = self._montar_slides_para_copy(slides)
        assert "tipo_layout" not in result[0]

    def test_tipo_capa_conteudo_cta_correto(self):
        slides = [
            {"principal": "Slide1", "alternativo": ""},
            {"principal": "Slide2", "alternativo": ""},
            {"principal": "Slide3", "alternativo": ""},
        ]
        result = self._montar_slides_para_copy(slides)
        assert result[0]["tipo"] == "capa"
        assert result[1]["tipo"] == "conteudo"
        assert result[2]["tipo"] == "cta"

    def test_indice_comexa_em_1(self):
        slides = [
            {"principal": "A", "alternativo": ""},
            {"principal": "B", "alternativo": ""},
        ]
        result = self._montar_slides_para_copy(slides)
        assert result[0]["indice"] == 1
        assert result[1]["indice"] == 2

    def test_com_pydantic_model(self):
        """Testa com objetos SlideTextoPronto reais (getattr path)."""
        from dtos.pipeline.criar_pipeline.request import SlideTextoPronto
        slides = [
            SlideTextoPronto(principal="Capa", tipo_layout="texto"),
            SlideTextoPronto(principal="Body", tipo_layout="lista"),
        ]
        result = self._montar_slides_para_copy(slides)
        assert result[0]["tipo_layout"] == "texto"
        assert result[1]["tipo_layout"] == "lista"
