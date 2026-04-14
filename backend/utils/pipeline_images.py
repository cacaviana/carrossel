"""Salva e carrega imagens de pipeline no disco ao inves de base64 no banco.

Estrutura: assets/pipeline-images/{pipeline_id}/slide-01.png
"""
import base64
from io import BytesIO
from pathlib import Path

IMAGES_DIR = Path(__file__).parent.parent / "assets" / "pipeline-images"


def _strip_data_uri(b64: str) -> str:
    """Remove prefixo data URI (data:image/...;base64,) se presente."""
    return b64.split(",", 1)[1] if "," in b64 else b64


def salvar_imagem(pipeline_id: str, slide_index: int, image_b64: str, formato: str = "carrossel") -> str:
    """Salva imagem base64 como PNG no disco.

    PNG mantém qualidade máxima pro pipeline. A exportação final (PDF/Drive)
    pode comprimir se necessário.
    """
    pipeline_dir = IMAGES_DIR / pipeline_id
    pipeline_dir.mkdir(parents=True, exist_ok=True)
    filename = f"slide-{slide_index:02d}.png"
    path = pipeline_dir / filename
    raw = _strip_data_uri(image_b64)
    img_bytes = base64.b64decode(raw)

    # Validacao: rejeita bytes que nao comecam com magic number de imagem
    _PNG_MAGIC = b"\x89PNG"
    _JPEG_MAGIC = b"\xff\xd8\xff"
    _WEBP_MAGIC = b"RIFF"
    if not (img_bytes[:4] == _PNG_MAGIC or img_bytes[:3] == _JPEG_MAGIC or img_bytes[:4] == _WEBP_MAGIC):
        print(f"[pipeline_images] WARN slide-{slide_index:02d}: bytes nao comecam com magic number valido (hex: {img_bytes[:16].hex()}). Possivel data URI nao removido.")

    try:
        from PIL import Image
        img = Image.open(BytesIO(img_bytes))
        img.verify()
        # Re-abrir apos verify (verify invalida o objeto)
        img = Image.open(BytesIO(img_bytes))
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        # Ajusta pro tamanho do formato sem distorcer (resize + crop central)
        from utils.dimensions import get_dims
        dims = get_dims(formato)
        target_w, target_h = dims["width"], dims["height"]
        if img.width != target_w or img.height != target_h:
            # Escala pra cobrir o target mantendo proporção
            scale = max(target_w / img.width, target_h / img.height)
            new_w = int(img.width * scale)
            new_h = int(img.height * scale)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            # Crop central pro tamanho exato
            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            img = img.crop((left, top, left + target_w, top + target_h))

        img.save(path, "PNG")
    except Exception as e:
        print(f"[pipeline_images] ERRO slide-{slide_index:02d}: imagem corrompida ({e}). Bytes descartados.")
        return ""

    # Pos-save: confirma que o PNG salvo eh valido
    try:
        from PIL import Image
        img_check = Image.open(path)
        img_check.verify()
    except Exception as e:
        print(f"[pipeline_images] ERRO slide-{slide_index:02d}: PNG salvo falhou verify ({e})")
        path.unlink(missing_ok=True)
        return ""

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
