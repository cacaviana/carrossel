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

# Pools de referencia visual (Fase 1)
POOL_COM_AVATAR = "com_avatar"
POOL_SEM_AVATAR = "sem_avatar"
VALID_POOLS = {POOL_COM_AVATAR, POOL_SEM_AVATAR}


def detectar_pool(nome: str) -> str | None:
    """Detecta pool do asset a partir do prefixo do nome.

    Convencao:
        ref_ca_*  -> pool com_avatar (refs que mostram a pessoa)
        ref_sa_*  -> pool sem_avatar (refs puramente visuais)
        ref_*     -> pool com_avatar (legado, migra invisivel)
        outros    -> None (nao eh ref, eh avatar ou foto)
    """
    if nome.startswith("ref_ca_"):
        return POOL_COM_AVATAR
    if nome.startswith("ref_sa_"):
        return POOL_SEM_AVATAR
    if nome.startswith("ref_"):
        return POOL_COM_AVATAR
    return None


def _aplicar_prefixo_pool(nome: str, pool: str) -> str:
    """Remove prefixo anterior (ref_ca_/ref_sa_/ref_) e aplica o do pool."""
    base = nome
    for prefix in ("ref_ca_", "ref_sa_", "ref_"):
        if base.startswith(prefix):
            base = base[len(prefix):]
            break
    return f"ref_ca_{base}" if pool == POOL_COM_AVATAR else f"ref_sa_{base}"


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
    try:
        col = _get_assets_col()
        if col:
            col.update_one(
                {"slug": slug, "nome": "__foto__"},
                {"$set": {"slug": slug, "nome": "__foto__", "data_uri": data_uri, "is_referencia": False}},
                upsert=True,
            )
    except Exception as e:
        print(f"[brand_service] Erro MongoDB salvar_foto: {e}")

    # Disco (fallback local)
    try:
        FOTOS_DIR.mkdir(exist_ok=True)
        (FOTOS_DIR / f"{slug}.jpg").write_bytes(b64.b64decode(raw))
    except Exception:
        pass

    return {"slug": slug, "foto": data_uri}


def buscar_foto_brand(slug: str) -> dict:
    """Busca foto da marca: MongoDB primeiro, disco como fallback."""
    try:
        col = _get_assets_col()
        if col:
            doc = col.find_one({"slug": slug, "nome": "__foto__"}, {"_id": 0})
            if doc and doc.get("data_uri"):
                return {"foto": doc["data_uri"]}
    except Exception:
        pass

    try:
        for ext in ("jpg", "png", "jpeg"):
            path = FOTOS_DIR / f"{slug}.{ext}"
            if path.exists():
                data = b64.b64encode(path.read_bytes()).decode()
                mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
                return {"foto": f"data:{mime};base64,{data}"}
    except Exception:
        pass
    return {"foto": None}


def buscar_foto_brand_b64(slug: str) -> str | None:
    """Retorna foto como data URI base64 (uso interno)."""
    result = buscar_foto_brand(slug)
    return result.get("foto")


def listar_assets(slug: str) -> dict:
    """Lista assets: MongoDB primeiro, disco como fallback.

    Cada item retorna o campo `pool` detectado pelo prefixo do nome:
    'com_avatar' | 'sem_avatar' | None (se eh avatar/foto).
    """
    items = []

    try:
        col = _get_assets_col()
        if col:
            docs = list(col.find({"slug": slug}, {"_id": 0}))
            for doc in docs:
                if doc.get("nome") == "__foto__":
                    continue
                nome = doc["nome"]
                items.append({
                    "nome": nome,
                    "arquivo": f"{nome}.jpg",
                    "preview": doc.get("data_uri", ""),
                    "is_referencia": doc.get("is_referencia", nome.startswith("ref_")),
                    "pool": detectar_pool(nome),
                })
    except Exception:
        pass

    # Fallback disco (local dev)
    if not items:
        try:
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
                            "pool": detectar_pool(f.stem),
                        })
        except Exception:
            pass

    return {"assets": items, "total": len(items)}


def definir_referencia(slug: str, nome_asset: str | None) -> dict | None:
    """Define qual asset eh a referencia visual para geracao de imagens."""
    brand = carregar_brand(slug)
    if not brand:
        return None
    brand["referencia_imagem"] = nome_asset
    _salvar_brand(slug, brand, overwrite=True)
    return {"slug": slug, "referencia_imagem": nome_asset}


def upload_asset(slug: str, nome: str, imagem: str, pool: str | None = None) -> dict:
    """Salva asset no MongoDB (e disco como fallback).

    Args:
        slug: brand slug
        nome: nome do asset. Se `pool` for passado, o nome eh automaticamente
              prefixado com ref_ca_ ou ref_sa_ (substituindo prefixo existente).
        imagem: base64 data URI
        pool: 'com_avatar' | 'sem_avatar' | None. Se None, usa o `nome` como veio
              (compat com upload de avatar/foto que nao eh ref).

    Raises:
        ValueError: se pool invalido
    """
    if pool is not None:
        if pool not in VALID_POOLS:
            raise ValueError(f"pool invalido: {pool}. Use 'com_avatar' ou 'sem_avatar'")
        nome = _aplicar_prefixo_pool(nome, pool)

    raw = imagem.split(",")[1] if "," in imagem else imagem
    ext = "png"
    mime = "image/png"
    if imagem.startswith("data:image/jpeg") or imagem.startswith("data:image/jpg"):
        ext = "jpg"
        mime = "image/jpeg"
    data_uri = f"data:{mime};base64,{raw}"

    # MongoDB (persistente)
    saved = False
    try:
        col = _get_assets_col()
        if col:
            col.update_one(
                {"slug": slug, "nome": nome},
                {"$set": {"slug": slug, "nome": nome, "data_uri": data_uri, "is_referencia": nome.startswith("ref_")}},
                upsert=True,
            )
            saved = True
    except Exception as e:
        print(f"[brand_service] Erro MongoDB upload_asset: {e}")

    # Disco (fallback)
    try:
        assets_dir = BRAND_ASSETS_DIR / slug
        assets_dir.mkdir(parents=True, exist_ok=True)
        (assets_dir / f"{nome}.{ext}").write_bytes(b64.b64decode(raw))
        saved = True
    except Exception:
        pass

    if not saved:
        raise RuntimeError("Nao foi possivel salvar o asset")

    return {"nome": nome, "arquivo": f"{nome}.{ext}", "pool": detectar_pool(nome)}


def deletar_asset(slug: str, nome: str) -> dict | None:
    """Deleta asset do MongoDB e do disco."""
    deleted = False
    try:
        col = _get_assets_col()
        if col:
            result = col.delete_one({"slug": slug, "nome": nome})
            if result.deleted_count > 0:
                deleted = True
    except Exception:
        pass

    try:
        assets_dir = BRAND_ASSETS_DIR / slug
        for f in assets_dir.glob(f"{nome}.*"):
            f.unlink()
            deleted = True
    except Exception:
        pass

    return {"deletado": nome} if deleted else None
