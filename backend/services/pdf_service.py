"""Gera PDF do carrossel LinkedIn — uma imagem por pagina (1080x1350, 4:5)."""

import base64
import io
import tempfile
from pathlib import Path

from fpdf import FPDF
from PIL import Image


def gerar_pdf_from_images(images_base64: list[str | None]) -> str:
    """Recebe lista de imagens base64, retorna PDF base64.

    Cada imagem vira uma pagina no PDF com proporcao 4:5 (1080x1350).
    Dimensoes da pagina em mm: 216mm x 270mm (mantendo 4:5).
    """
    # Pagina 4:5 em mm (1080/1350 * 270 = 216)
    PAGE_W = 216.0
    PAGE_H = 270.0

    pdf = FPDF(unit="mm", format=(PAGE_W, PAGE_H))
    pdf.set_auto_page_break(auto=False)

    tmp_files: list[str] = []

    for i, img_b64 in enumerate(images_base64):
        if not img_b64:
            continue

        # Remove prefixo data:image/...;base64, se presente
        if "," in img_b64:
            img_b64 = img_b64.split(",", 1)[1]

        img_bytes = base64.b64decode(img_b64)

        # Salva como PNG temporario para fpdf
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.write(img_bytes)
        tmp.close()
        tmp_files.append(tmp.name)

        pdf.add_page()
        pdf.image(tmp.name, x=0, y=0, w=PAGE_W, h=PAGE_H)

    # Gera PDF em memoria
    pdf_bytes = pdf.output()

    # Limpa arquivos temporarios
    for f in tmp_files:
        Path(f).unlink(missing_ok=True)

    return base64.b64encode(pdf_bytes).decode("utf-8")
