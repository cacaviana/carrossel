"""Testes unitarios para utils/pipeline_images.py

Testa:
- _strip_data_uri: remocao de prefixo data URI
- salvar_imagem: validacao de magic bytes, verify PIL, rejeicao de corrompidos
- carregar_imagem_b64: carregamento e formatacao base64
"""
import base64
import sys
from io import BytesIO
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.pipeline_images import _strip_data_uri, salvar_imagem, carregar_imagem_b64, caminho_absoluto


# --- _strip_data_uri ---

class TestStripDataUri:
    def test_remove_data_uri_prefix_png(self):
        raw = "data:image/png;base64,iVBORw0KGgo="
        assert _strip_data_uri(raw) == "iVBORw0KGgo="

    def test_remove_data_uri_prefix_jpeg(self):
        raw = "data:image/jpeg;base64,/9j/4AAQ"
        assert _strip_data_uri(raw) == "/9j/4AAQ"

    def test_no_prefix_returns_same(self):
        raw = "iVBORw0KGgoAAAANSUhEUg=="
        assert _strip_data_uri(raw) == raw

    def test_empty_string(self):
        assert _strip_data_uri("") == ""

    def test_multiple_commas_splits_on_first(self):
        raw = "data:image/png;base64,abc,def"
        assert _strip_data_uri(raw) == "abc,def"


# --- salvar_imagem ---

class TestSalvarImagem:
    def _make_valid_png_b64(self, width=100, height=125):
        """Cria um PNG valido em base64 usando PIL."""
        from PIL import Image
        img = Image.new("RGB", (width, height), color=(0, 100, 200))
        buf = BytesIO()
        img.save(buf, "PNG")
        return base64.b64encode(buf.getvalue()).decode()

    def _make_valid_jpeg_b64(self):
        """Cria JPEG valido em base64."""
        from PIL import Image
        img = Image.new("RGB", (100, 100), color=(255, 0, 0))
        buf = BytesIO()
        img.save(buf, "JPEG")
        return base64.b64encode(buf.getvalue()).decode()

    def test_salva_png_valido(self, tmp_path):
        b64 = self._make_valid_png_b64(1080, 1350)
        with patch("utils.pipeline_images.IMAGES_DIR", tmp_path):
            result = salvar_imagem("test-pipe-1", 1, b64)
        assert result == "pipeline-images/test-pipe-1/slide-01.png"
        assert (tmp_path / "test-pipe-1" / "slide-01.png").exists()

    def test_salva_jpeg_valido(self, tmp_path):
        b64 = self._make_valid_jpeg_b64()
        with patch("utils.pipeline_images.IMAGES_DIR", tmp_path):
            result = salvar_imagem("test-pipe-2", 3, b64)
        assert result == "pipeline-images/test-pipe-2/slide-03.png"
        # Resultado eh salvo como PNG independente do input
        assert (tmp_path / "test-pipe-2" / "slide-03.png").exists()

    def test_aceita_data_uri_prefix(self, tmp_path):
        b64_raw = self._make_valid_png_b64(1080, 1350)
        b64_with_prefix = f"data:image/png;base64,{b64_raw}"
        with patch("utils.pipeline_images.IMAGES_DIR", tmp_path):
            result = salvar_imagem("test-pipe-3", 1, b64_with_prefix)
        assert result != ""
        assert "slide-01.png" in result

    def test_rejeita_bytes_corrompidos(self, tmp_path):
        # Bytes aleatorios que nao sao imagem valida
        garbage = base64.b64encode(b"this is not an image at all!!! garbage bytes").decode()
        with patch("utils.pipeline_images.IMAGES_DIR", tmp_path):
            result = salvar_imagem("test-pipe-4", 1, garbage)
        assert result == ""

    def test_slide_index_formatado_com_zero(self, tmp_path):
        b64 = self._make_valid_png_b64(1080, 1350)
        with patch("utils.pipeline_images.IMAGES_DIR", tmp_path):
            result = salvar_imagem("pipe-x", 9, b64)
        assert "slide-09.png" in result

    def test_cria_diretorio_se_nao_existe(self, tmp_path):
        b64 = self._make_valid_png_b64(1080, 1350)
        with patch("utils.pipeline_images.IMAGES_DIR", tmp_path):
            salvar_imagem("novo-pipeline", 1, b64)
        assert (tmp_path / "novo-pipeline").is_dir()

    def test_imagem_pequena_redimensionada(self, tmp_path):
        """Imagem < 800px largura deve ser redimensionada."""
        b64 = self._make_valid_png_b64(400, 500)  # ratio 4:5
        with patch("utils.pipeline_images.IMAGES_DIR", tmp_path):
            result = salvar_imagem("pipe-resize", 1, b64)
        assert result != ""
        from PIL import Image
        saved = Image.open(tmp_path / "pipe-resize" / "slide-01.png")
        assert saved.width == 1080


# --- carregar_imagem_b64 ---

class TestCarregarImagemB64:
    def test_retorna_none_se_nao_existe(self, tmp_path):
        with patch("utils.pipeline_images.IMAGES_DIR", tmp_path / "images"):
            result = carregar_imagem_b64("pipeline-images/fake/slide-01.png")
        assert result is None

    def test_carrega_e_retorna_data_uri(self, tmp_path):
        # Criar arquivo de imagem fake
        img_dir = tmp_path / "pipeline-images" / "test1"
        img_dir.mkdir(parents=True)
        img_file = img_dir / "slide-01.png"
        from PIL import Image
        img = Image.new("RGB", (100, 100))
        img.save(img_file, "PNG")

        with patch("utils.pipeline_images.IMAGES_DIR", tmp_path / "pipeline-images"):
            result = carregar_imagem_b64("pipeline-images/test1/slide-01.png")
        assert result is not None
        assert result.startswith("data:image/png;base64,")


# --- caminho_absoluto ---

class TestCaminhoAbsoluto:
    def test_retorna_none_se_nao_existe(self, tmp_path):
        with patch("utils.pipeline_images.IMAGES_DIR", tmp_path / "images"):
            result = caminho_absoluto("pipeline-images/fake/slide-01.png")
        assert result is None

    def test_retorna_path_se_existe(self, tmp_path):
        img_dir = tmp_path / "pipeline-images" / "test1"
        img_dir.mkdir(parents=True)
        img_file = img_dir / "slide-01.png"
        img_file.write_bytes(b"fake")
        with patch("utils.pipeline_images.IMAGES_DIR", tmp_path / "pipeline-images"):
            result = caminho_absoluto("pipeline-images/test1/slide-01.png")
        assert result is not None
        assert result.exists()
