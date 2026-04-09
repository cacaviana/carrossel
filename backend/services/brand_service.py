"""Service de brands — lógica de negócio extraída do router config.py."""

import base64 as b64
from pathlib import Path

from services.brand_prompt_builder import (
    carregar_brand,
    deletar_brand as _deletar_brand,
    listar_brands as _listar_brands,
    salvar_brand as _salvar_brand,
)

ASSETS_ROOT = Path(__file__).parent.parent / "assets"
FOTOS_DIR = ASSETS_ROOT / "fotos"
BRAND_ASSETS_DIR = ASSETS_ROOT / "brand-assets"


def listar_brands() -> list[dict]:
    brands = _listar_brands()
    result = []
    for b in brands:
        full = carregar_brand(b["slug"])
        result.append({
            "slug": b["slug"],
            "nome": b["nome"],
            "cor_principal": full.get("cores", {}).get("acento_principal", "") if full else "",
            "cor_fundo": full.get("cores", {}).get("fundo", "") if full else "",
        })
    return result


def buscar_brand(slug: str) -> dict | None:
    return carregar_brand(slug)


def criar_brand(slug: str, data: dict) -> dict:
    """Cria brand novo. Raises FileExistsError se já existe."""
    return _salvar_brand(slug, data)


def atualizar_brand(slug: str, data: dict) -> dict | None:
    """Atualiza brand existente. Retorna None se não encontrado."""
    if not carregar_brand(slug):
        return None
    data["slug"] = slug
    return _salvar_brand(slug, data, overwrite=True)


def deletar_brand_service(slug: str) -> bool:
    return _deletar_brand(slug)


def clonar_brand(slug_origem: str, slug_destino: str, nome_destino: str) -> dict:
    """Clona uma marca existente com novo slug e nome. Copia JSON, foto e assets."""
    import re
    import shutil

    # Sanitizar slug: minusculo, sem espacos, so alfanumerico e hifen
    slug_destino = re.sub(r'[^a-z0-9-]', '', slug_destino.lower().replace(' ', '-'))
    if not slug_destino:
        raise ValueError("Slug invalido")

    original = carregar_brand(slug_origem)
    if not original:
        raise ValueError(f"Marca '{slug_origem}' nao encontrada")
    if carregar_brand(slug_destino):
        raise FileExistsError(f"Marca '{slug_destino}' ja existe")

    # Clonar JSON com novo slug e nome
    clone = {**original, "slug": slug_destino, "nome": nome_destino}
    _salvar_brand(slug_destino, clone)

    # Clonar foto
    FOTOS_DIR.mkdir(exist_ok=True)
    for ext in ("jpg", "png", "jpeg"):
        foto_orig = FOTOS_DIR / f"{slug_origem}.{ext}"
        if foto_orig.exists():
            shutil.copy2(foto_orig, FOTOS_DIR / f"{slug_destino}.{ext}")
            break

    # Clonar assets
    assets_orig = BRAND_ASSETS_DIR / slug_origem
    assets_dest = BRAND_ASSETS_DIR / slug_destino
    if assets_orig.exists():
        shutil.copytree(assets_orig, assets_dest, dirs_exist_ok=True)

    return {"slug": slug_destino, "nome": nome_destino, "mensagem": f"Marca '{nome_destino}' clonada de '{slug_origem}'"}


def salvar_foto_brand(slug: str, foto_data: str) -> dict:
    """Decodifica base64 e salva foto no disco. Retorna {slug, foto}."""
    raw = foto_data.split(",")[1] if "," in foto_data else foto_data
    FOTOS_DIR.mkdir(exist_ok=True)
    foto_path = FOTOS_DIR / f"{slug}.jpg"
    foto_path.write_bytes(b64.b64decode(raw))
    return {"slug": slug, "foto": str(foto_path)}


def buscar_foto_brand(slug: str) -> dict:
    """Retorna URL da foto da marca. Retorna {foto: None} se não encontrada."""
    for ext in ("jpg", "png", "jpeg"):
        path = FOTOS_DIR / f"{slug}.{ext}"
        if path.exists():
            return {"foto": f"/api/brands/{slug}/foto/file"}
    return {"foto": None}


def buscar_foto_brand_b64(slug: str) -> str | None:
    """Retorna foto como base64 (uso interno — overlay, Gemini, etc)."""
    for ext in ("jpg", "png", "jpeg"):
        path = FOTOS_DIR / f"{slug}.{ext}"
        if path.exists():
            data = b64.b64encode(path.read_bytes()).decode()
            mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
            return f"data:{mime};base64,{data}"
    return None


def listar_assets(slug: str) -> dict:
    assets_dir = BRAND_ASSETS_DIR / slug
    assets_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for f in sorted(assets_dir.glob("*.*")):
        if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            items.append({
                "nome": f.stem,
                "arquivo": f.name,
                "preview": f"/api/brands/{slug}/assets/{f.stem}/file",
                "is_referencia": f.stem.startswith("ref_"),
            })
    return {"assets": items, "total": len(items)}


def definir_referencia(slug: str, nome_asset: str | None) -> dict | None:
    """Define qual asset é a referência visual para geração de imagens.
    Se nome_asset=None, remove a referência."""
    brand = carregar_brand(slug)
    if not brand:
        return None
    if nome_asset:
        assets_dir = BRAND_ASSETS_DIR / slug
        found = list(assets_dir.glob(f"{nome_asset}.*"))
        if not found:
            return None
        brand["referencia_imagem"] = f"brand-assets/{slug}/{found[0].name}"
    else:
        brand["referencia_imagem"] = None
    _salvar_brand(slug, brand, overwrite=True)
    return {"slug": slug, "referencia_imagem": brand["referencia_imagem"]}


def upload_asset(slug: str, nome: str, imagem: str) -> dict:
    """Salva asset no disco. Retorna {nome, arquivo}."""
    assets_dir = BRAND_ASSETS_DIR / slug
    assets_dir.mkdir(parents=True, exist_ok=True)
    raw = imagem.split(",")[1] if "," in imagem else imagem
    ext = "png"
    if imagem.startswith("data:image/jpeg") or imagem.startswith("data:image/jpg"):
        ext = "jpg"
    path = assets_dir / f"{nome}.{ext}"
    path.write_bytes(b64.b64decode(raw))
    return {"nome": nome, "arquivo": path.name}


def deletar_asset(slug: str, nome: str) -> dict | None:
    """Deleta asset do disco. Retorna {deletado} ou None se não encontrado."""
    assets_dir = BRAND_ASSETS_DIR / slug
    for f in assets_dir.glob(f"{nome}.*"):
        f.unlink()
        return {"deletado": nome}
    return None
