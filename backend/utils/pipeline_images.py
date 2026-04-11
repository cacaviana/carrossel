"""Salva e carrega imagens de pipeline no disco ao inves de base64 no banco.

Estrutura: assets/pipeline-images/{pipeline_id}/slide-01.png
"""
import base64
from io import BytesIO
from pathlib import Path

IMAGES_DIR = Path(__file__).parent.parent / "assets" / "pipeline-images"


def salvar_imagem(pipeline_id: str, slide_index: int, image_b64: str) -> str:
    """Salva imagem base64 como PNG real no disco.

    Gemini pode retornar JPEG mesmo quando pedimos PNG — por isso sempre
    decodificamos via PIL e re-encodamos como PNG, garantindo que a extensao
    `.png` corresponda aos bytes reais (magic bytes 89 50 4E 47).
    """
    pipeline_dir = IMAGES_DIR / pipeline_id
    pipeline_dir.mkdir(parents=True, exist_ok=True)
    filename = f"slide-{slide_index:02d}.png"
    path = pipeline_dir / filename
    raw = image_b64.split(",")[1] if "," in image_b64 else image_b64
    img_bytes = base64.b64decode(raw)

    try:
        from PIL import Image
        img = Image.open(BytesIO(img_bytes))
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        # Se a imagem saiu muito pequena (< 800px largura), redimensiona pra 1080x1350
        if img.width < 800:
            target_ratio = 4 / 5
            current_ratio = img.width / img.height
            if abs(current_ratio - target_ratio) < 0.15:
                img = img.resize((1080, 1350), Image.LANCZOS)
            else:
                scale = 1080 / img.width
                new_h = int(img.height * scale)
                img = img.resize((1080, new_h), Image.LANCZOS)

        img.save(path, "PNG")
    except Exception as e:
        # Fallback: escreve bytes crus pra nao perder a imagem do usuario
        print(f"[pipeline_images] PIL falhou ({e}), salvando bytes crus")
        path.write_bytes(img_bytes)

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
