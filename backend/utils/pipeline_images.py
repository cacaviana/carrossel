"""Salva e carrega imagens de pipeline no disco ao inves de base64 no banco.

Estrutura: assets/pipeline-images/{pipeline_id}/slide-01.png
"""
import base64
from pathlib import Path

IMAGES_DIR = Path(__file__).parent.parent / "assets" / "pipeline-images"


def salvar_imagem(pipeline_id: str, slide_index: int, image_b64: str) -> str:
    """Salva imagem base64 como PNG no disco. Retorna path relativo."""
    pipeline_dir = IMAGES_DIR / pipeline_id
    pipeline_dir.mkdir(parents=True, exist_ok=True)
    filename = f"slide-{slide_index:02d}.png"
    path = pipeline_dir / filename
    raw = image_b64.split(",")[1] if "," in image_b64 else image_b64
    path.write_bytes(base64.b64decode(raw))
    return f"pipeline-images/{pipeline_id}/{filename}"


def carregar_imagem_b64(path_rel: str) -> str | None:
    """Carrega imagem do disco como base64. Aceita path relativo."""
    full = IMAGES_DIR.parent / path_rel
    if not full.exists():
        return None
    data = base64.b64encode(full.read_bytes()).decode()
    return f"data:image/png;base64,{data}"


def caminho_absoluto(path_rel: str) -> Path | None:
    """Retorna Path absoluto do arquivo. None se nao existe."""
    full = IMAGES_DIR.parent / path_rel
    return full if full.exists() else None
