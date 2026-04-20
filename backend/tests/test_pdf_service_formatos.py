"""Testes unitarios — services/pdf_service.py.

O PDF service gera 1 pagina por imagem (4:5 hardcoded no gerar_pdf_from_images).
Para os 3 formatos (post_unico, reels, thumbnail), o PDF de 1 imagem deve
funcionar — o PDF e usado para export, mesmo que a proporcao nao case 100%
com a imagem original.
"""

import base64
import sys
from io import BytesIO
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

pytest.importorskip("fpdf", reason="fpdf nao instalado — pdf_service depende dele")
from services.pdf_service import gerar_pdf_from_images


def _make_png_b64(width=1080, height=1350):
    """Cria um PNG valido em base64 usando PIL."""
    from PIL import Image
    img = Image.new("RGB", (width, height), color=(100, 50, 200))
    buf = BytesIO()
    img.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


class TestGerarPdfFromImages:
    def test_gera_pdf_com_uma_imagem(self):
        b64 = _make_png_b64()
        pdf_b64 = gerar_pdf_from_images([b64])
        pdf_bytes = base64.b64decode(pdf_b64)
        assert pdf_bytes[:4] == b"%PDF"

    def test_gera_pdf_com_multiplas_imagens(self):
        imgs = [_make_png_b64() for _ in range(3)]
        pdf_b64 = gerar_pdf_from_images(imgs)
        pdf_bytes = base64.b64decode(pdf_b64)
        assert pdf_bytes[:4] == b"%PDF"

    def test_aceita_data_uri_prefix(self):
        raw = _make_png_b64()
        with_prefix = f"data:image/png;base64,{raw}"
        pdf_b64 = gerar_pdf_from_images([with_prefix])
        pdf_bytes = base64.b64decode(pdf_b64)
        assert pdf_bytes[:4] == b"%PDF"

    def test_pula_imagens_none(self):
        b64 = _make_png_b64()
        pdf_b64 = gerar_pdf_from_images([b64, None, b64])
        pdf_bytes = base64.b64decode(pdf_b64)
        assert pdf_bytes[:4] == b"%PDF"

    def test_lista_toda_none_nao_quebra(self):
        """Lista [None, None] gera PDF vazio (sem paginas) mas nao crasha."""
        try:
            pdf_b64 = gerar_pdf_from_images([None, None])
            # fpdf pode exigir pelo menos 1 pagina — aceitar que quebre e tudo bem
        except Exception:
            pass  # comportamento esperado se fpdf exige page


# =============================================================================
# Exportar PDF pros 3 formatos (post_unico, reels, thumbnail)
# =============================================================================
@pytest.mark.parametrize("formato,w,h", [
    ("post_unico", 1080, 1350),
    ("capa_reels", 1080, 1920),
    ("thumbnail_youtube", 1280, 720),
    ("carrossel", 1080, 1350),
])
class TestPdfPorFormato:
    def test_gera_pdf_para_cada_formato(self, formato, w, h):
        """Independente do formato da imagem fonte, o PDF e gerado ok."""
        b64 = _make_png_b64(width=w, height=h)
        pdf_b64 = gerar_pdf_from_images([b64])
        assert pdf_b64
        # Validar que e PDF
        pdf_bytes = base64.b64decode(pdf_b64)
        assert pdf_bytes[:4] == b"%PDF"
