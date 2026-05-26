"""Testes unitarios — mappers/imagem_mapper.py.

extract_image_from_response converte resposta da API Gemini em data URI base64.
Usado pelos 3 formatos (post_unico, capa_reels, thumbnail_youtube) — o mapper
e identico pros 3.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mappers.imagem_mapper import extract_image_from_response


def _gemini_response(b64: str = "AAAABBBB", mime: str = "image/png"):
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"inlineData": {"data": b64, "mimeType": mime}}
                    ]
                }
            }
        ]
    }


class TestExtractImage:
    def test_retorna_data_uri(self):
        resp = _gemini_response("FOOBAR")
        result = extract_image_from_response(resp)
        assert result == "data:image/png;base64,FOOBAR"

    def test_mime_default_png_se_faltar(self):
        resp = {
            "candidates": [
                {"content": {"parts": [{"inlineData": {"data": "X"}}]}}
            ]
        }
        result = extract_image_from_response(resp)
        assert result == "data:image/png;base64,X"

    def test_mime_customizado(self):
        resp = _gemini_response("X", mime="image/jpeg")
        result = extract_image_from_response(resp)
        assert result == "data:image/jpeg;base64,X"

    def test_retorna_none_sem_candidates(self):
        assert extract_image_from_response({}) is None
        assert extract_image_from_response({"candidates": []}) is None

    def test_retorna_none_sem_inline_data(self):
        resp = {
            "candidates": [
                {"content": {"parts": [{"text": "bla"}]}}
            ]
        }
        assert extract_image_from_response(resp) is None

    def test_retorna_none_sem_parts(self):
        resp = {"candidates": [{"content": {}}]}
        assert extract_image_from_response(resp) is None

    def test_ignora_partes_text_e_pega_inline(self):
        """Gemini pode vir text + inlineData — precisamos pegar a imagem."""
        resp = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "aqui esta a imagem"},
                            {"inlineData": {"data": "BASE64", "mimeType": "image/png"}},
                        ]
                    }
                }
            ]
        }
        result = extract_image_from_response(resp)
        assert result == "data:image/png;base64,BASE64"


@pytest.mark.parametrize("formato", ["post_unico", "capa_reels", "thumbnail_youtube", "carrossel"])
class TestExtractPorFormato:
    """Mapper e agnostico ao formato — o teste aqui e simbolico."""

    def test_extrai_imagem_para_qualquer_formato(self, formato):
        resp = _gemini_response(f"B64_{formato}")
        result = extract_image_from_response(resp)
        assert result is not None
        assert formato in result
