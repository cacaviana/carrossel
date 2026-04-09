"""Service de brands — lógica de negócio extraída do router config.py.

Assets e fotos salvos no MongoDB (persistente) com fallback pro disco (dev local).
"""

import base64 as b64
from pathlib import Path

from data.connections.mongo_connection import get_mongo_db
from services.brand_prompt_builder import (
    carregar_brand,
    deletar_brand as _deletar_brand,
    listar_brands as _listar_brands,
    salvar_brand as _salvar_brand,
)

ASSETS_ROOT = Path(__file__).parent.parent / "assets"
FOTOS_DIR = ASSETS_ROOT / "fotos"
BRAND_ASSETS_DIR = ASSETS_ROOT / "brand-assets"


def _get_assets_col():
    db = get_mongo_db()
    return db["brand_assets"] if db else None


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
    """Salva foto no MongoDB (e disco como fallback)."""
    raw = foto_data.split(",")[1] if "," in foto_data else foto_data
    mime = "image/jpeg"
    if foto_data.startswith("data:image/png"):
        mime = "image/png"
    data_uri = f"data:{mime};base64,{raw}"

    # MongoDB (persistente)
    col = _get_assets_col()
    if col:
        col.update_one(
            {"slug": slug, "nome": "__foto__"},
            {"$set": {"slug": slug, "nome": "__foto__", "data_uri": data_uri, "is_referencia": False}},
            upsert=True,
        )

    # Disco (fallback local)
    try:
        FOTOS_DIR.mkdir(exist_ok=True)
        (FOTOS_DIR / f"{slug}.jpg").write_bytes(b64.b64decode(raw))
    except Exception:
        pass

    return {"slug": slug, "foto": data_uri}


def buscar_foto_brand(slug: str) -> dict:
    """Busca foto da marca: MongoDB primeiro, disco como fallback."""
    col = _get_assets_col()
    if col:
        doc = col.find_one({"slug": slug, "nome": "__foto__"}, {"_id": 0})
        if doc and doc.get("data_uri"):
            return {"foto": doc["data_uri"]}

    for ext in ("jpg", "png", "jpeg"):
        path = FOTOS_DIR / f"{slug}.{ext}"
        if path.exists():
            data = b64.b64encode(path.read_bytes()).decode()
            mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
            return {"foto": f"data:{mime};base64,{data}"}
    return {"foto": None}


def buscar_foto_brand_b64(slug: str) -> str | None:
    """Retorna foto como data URI base64 (uso interno)."""
    result = buscar_foto_brand(slug)
    return result.get("foto")


def listar_assets(slug: str) -> dict:
    """Lista assets: MongoDB primeiro, disco como fallback."""
    items = []

    col = _get_assets_col()
    if col:
        docs = col.find({"slug": slug, "nome": {"$ne": "__foto__"}}, {"_id": 0})
        for doc in docs:
            items.append({
                "nome": doc["nome"],
                "arquivo": f"{doc['nome']}.jpg",
                "preview": doc.get("data_uri", ""),
                "is_referencia": doc.get("is_referencia", doc["nome"].startswith("ref_")),
            })

    # Fallback disco (local dev)
    if not items:
        assets_dir = BRAND_ASSETS_DIR / slug
        if assets_dir.exists():
            for f in sorted(assets_dir.glob("*.*")):
                if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                    data = b64.b64encode(f.read_bytes()).decode()
                    mime = "image/jpeg" if f.suffix.lower() in (".jpg", ".jpeg") else "image/png"
                    items.append({
                        "nome": f.stem,
                        "arquivo": f.name,
                        "preview": f"data:{mime};base64,{data}",
                        "is_referencia": f.stem.startswith("ref_"),
                    })

    return {"assets": items, "total": len(items)}


def definir_referencia(slug: str, nome_asset: str | None) -> dict | None:
    """Define qual asset eh a referencia visual para geracao de imagens."""
    brand = carregar_brand(slug)
    if not brand:
        return None
    brand["referencia_imagem"] = nome_asset
    _salvar_brand(slug, brand, overwrite=True)
    return {"slug": slug, "referencia_imagem": nome_asset}


def upload_asset(slug: str, nome: str, imagem: str) -> dict:
    """Salva asset no MongoDB (e disco como fallback)."""
    raw = imagem.split(",")[1] if "," in imagem else imagem
    ext = "png"
    mime = "image/png"
    if imagem.startswith("data:image/jpeg") or imagem.startswith("data:image/jpg"):
        ext = "jpg"
        mime = "image/jpeg"
    data_uri = f"data:{mime};base64,{raw}"

    # MongoDB (persistente)
    col = _get_assets_col()
    if col:
        col.update_one(
            {"slug": slug, "nome": nome},
            {"$set": {"slug": slug, "nome": nome, "data_uri": data_uri, "is_referencia": nome.startswith("ref_")}},
            upsert=True,
        )

    # Disco (fallback local)
    try:
        assets_dir = BRAND_ASSETS_DIR / slug
        assets_dir.mkdir(parents=True, exist_ok=True)
        (assets_dir / f"{nome}.{ext}").write_bytes(b64.b64decode(raw))
    except Exception:
        pass

    return {"nome": nome, "arquivo": f"{nome}.{ext}"}


def deletar_asset(slug: str, nome: str) -> dict | None:
    """Deleta asset do MongoDB e do disco."""
    col = _get_assets_col()
    if col:
        result = col.delete_one({"slug": slug, "nome": nome})
        if result.deleted_count > 0:
            return {"deletado": nome}

    assets_dir = BRAND_ASSETS_DIR / slug
    for f in assets_dir.glob(f"{nome}.*"):
        f.unlink()
        return {"deletado": nome}
    return None
