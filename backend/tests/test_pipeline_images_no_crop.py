"""Regressao: pipeline_images.salvar_imagem NAO pode cortar (crop) nem esticar a imagem.

Contexto: antes o codigo fazia cover+crop quando ratio do Gemini divergia do target.
Isso cortava pedaco da imagem. O fix preserva a imagem original quando ratio nao bate.
"""

import base64
import io

import pytest
from PIL import Image

from utils.pipeline_images import salvar_imagem
from utils.dimensions import get_dims


def _png_b64(w: int, h: int, color=(80, 200, 120)) -> str:
    img = Image.new("RGB", (w, h), color)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _read_saved(path_rel: str, images_dir) -> Image.Image:
    """Abre PNG salvo. path_rel e 'pipeline-images/{id}/slide-01.png'.
    IMAGES_DIR aponta pro tmp_path, entao a pasta 'pipeline-images' fica sob ela."""
    from pathlib import Path
    full = Path(images_dir) / path_rel.replace("pipeline-images/", "")
    return Image.open(full)


class TestSalvarImagemSemCrop:

    def test_ratio_bate_e_tamanho_igual_preserva(self, tmp_path, monkeypatch):
        """Imagem 1080x1350 + target 1080x1350 → preserva como veio."""
        monkeypatch.setattr("utils.pipeline_images.IMAGES_DIR", tmp_path)
        b64 = _png_b64(1080, 1350)
        path = salvar_imagem("p-test-1", 1, b64, formato="carrossel")
        img = _read_saved(path, tmp_path)
        assert img.size == (1080, 1350)

    def test_ratio_bate_mas_menor_upscale(self, tmp_path, monkeypatch):
        """Gemini gerou 928x1152 (4:5), target 1080x1350 (4:5) → upscale limpo."""
        monkeypatch.setattr("utils.pipeline_images.IMAGES_DIR", tmp_path)
        b64 = _png_b64(928, 1152)
        path = salvar_imagem("p-test-2", 1, b64, formato="carrossel")
        img = _read_saved(path, tmp_path)
        assert img.size == (1080, 1350)

    def test_imagem_quadrada_em_formato_4x5_preserva_original_SEM_CROP(self, tmp_path, monkeypatch):
        """CASO CRITICO: Gemini gerou 1080x1080 (1:1) mas target eh 1080x1350 (4:5).
        NAO deve cortar pedaco da imagem nem esticar. Preserva tamanho original."""
        monkeypatch.setattr("utils.pipeline_images.IMAGES_DIR", tmp_path)
        b64 = _png_b64(1080, 1080)
        path = salvar_imagem("p-test-3", 1, b64, formato="carrossel")
        img = _read_saved(path, tmp_path)
        # Preservou 1080x1080 — nao cortou pra ficar 1080x1350
        assert img.size == (1080, 1080), (
            f"Esperava 1080x1080 preservado (sem crop), ganhou {img.size}"
        )

    def test_quadrado_1024_com_target_1080x1080_upscale(self, tmp_path, monkeypatch):
        """Gemini gerou 1024x1024 (1:1), target post_unico 1080x1080 (1:1) → upscale."""
        monkeypatch.setattr("utils.pipeline_images.IMAGES_DIR", tmp_path)

        # Mock get_dims pra simular post_unico como 1080x1080 (caso antigo que o designer
        # mencionou). No projeto atual post_unico ja migrou pra 1080x1350.
        import utils.dimensions as dm
        dm._json_cache = {"formatos": []}  # limpa cache
        monkeypatch.setattr(dm, "FORMATS", {"carrossel": {"width": 1080, "height": 1080, "ratio": "1:1", "label": "square"}})
        monkeypatch.setattr(dm, "_carregar_dims_mongo", lambda f: None)
        monkeypatch.setattr(dm, "_carregar_dims_json", lambda f: None)

        b64 = _png_b64(1024, 1024)
        path = salvar_imagem("p-test-4", 1, b64, formato="carrossel")
        img = _read_saved(path, tmp_path)
        assert img.size == (1080, 1080)

    def test_imagem_retrato_estranha_em_formato_4x5_preserva_original(self, tmp_path, monkeypatch):
        """Ratio 844x1264 (~0.667, mais alto que 4:5) + target 1080x1350 (0.8)
        → NAO corta, preserva original."""
        monkeypatch.setattr("utils.pipeline_images.IMAGES_DIR", tmp_path)
        b64 = _png_b64(844, 1264)
        path = salvar_imagem("p-test-5", 1, b64, formato="carrossel")
        img = _read_saved(path, tmp_path)
        # Nao cortou — ficou com tamanho original do Gemini
        assert img.size == (844, 1264)

    def test_reels_ratio_bate_upscale(self, tmp_path, monkeypatch):
        """720x1280 (9:16) + target capa_reels 1080x1920 (9:16) → upscale."""
        monkeypatch.setattr("utils.pipeline_images.IMAGES_DIR", tmp_path)
        b64 = _png_b64(720, 1280)
        path = salvar_imagem("p-test-6", 1, b64, formato="capa_reels")
        img = _read_saved(path, tmp_path)
        assert img.size == (1080, 1920)

    def test_imagem_nunca_ganha_barras_brancas(self, tmp_path, monkeypatch):
        """Se ratio nao bate, preserva tamanho original (sem letterbox).
        Gemini gera com cor dominante; adicionar barras brancas descaracteriza."""
        monkeypatch.setattr("utils.pipeline_images.IMAGES_DIR", tmp_path)
        b64 = _png_b64(1080, 1080, color=(200, 50, 50))  # vermelho dominante
        path = salvar_imagem("p-test-7", 1, b64, formato="carrossel")
        img = _read_saved(path, tmp_path)
        # Nao foi pra 1080x1350 com barras — preservou 1080x1080 vermelho inteiro
        assert img.size == (1080, 1080)
        # Confirma que sigue sendo vermelho no centro (nao tem barras)
        pixel_centro = img.convert("RGB").getpixel((540, 540))
        assert pixel_centro[0] > 150, "Centro da imagem nao deveria ter mudado"
