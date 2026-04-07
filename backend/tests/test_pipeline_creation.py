"""Testa a logica de criacao de pipeline com os 3 modos de entrada."""
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dtos.pipeline.criar_pipeline.request import CriarPipelineRequest


def test_request_modo_entrada_default_ideia():
    req = CriarPipelineRequest(tema="Um tema com mais de vinte caracteres para validar")
    assert req.modo_entrada == "ideia"


def test_request_modo_texto_pronto():
    req = CriarPipelineRequest(
        tema="Texto completo do post com mais de vinte caracteres",
        modo_entrada="texto_pronto",
    )
    assert req.modo_entrada == "texto_pronto"


def test_request_modo_disciplina():
    req = CriarPipelineRequest(
        tema="D7 - LangChain - Como usar RAG",
        modo_entrada="disciplina",
    )
    assert req.modo_entrada == "disciplina"


def test_request_tema_minimo_20_chars():
    with pytest.raises(Exception):
        CriarPipelineRequest(tema="curto")


def test_request_get_formato_default():
    req = CriarPipelineRequest(tema="Um tema com mais de vinte caracteres para validar")
    assert req.get_formato() == "carrossel"


def test_request_get_formato_from_formatos():
    req = CriarPipelineRequest(
        tema="Um tema com mais de vinte caracteres para validar",
        formatos=["post_unico", "carrossel"],
    )
    assert req.get_formato() == "post_unico"


def test_request_get_formato_explicit():
    req = CriarPipelineRequest(
        tema="Um tema com mais de vinte caracteres para validar",
        formato="thumbnail_youtube",
    )
    assert req.get_formato() == "thumbnail_youtube"
