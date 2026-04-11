"""Service de brands — logica de negocio de brand profile e assets.

Assets, fotos e logo ficam APENAS no MongoDB (sem fallback disco).
Disco eh efemero em deploy Azure/AWS — qualquer escrita local seria perdida
no proximo restart do container.

Como o Cosmos DB (compatibilidade Mongo) limita 2MB por documento, todo asset
eh comprimido pra JPEG quality 85 com max 1600px no lado maior antes de salvar.
"""

import base64 as b64
import io

from PIL import Image

from data.connections.mongo_connection import get_mongo_db
from services.brand_prompt_builder import (
    carregar_brand,
    deletar_brand as _deletar_brand,
    listar_brands as _listar_brands,
    salvar_brand as _salvar_brand,
)

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
    """Retorna Collection do Mongo ou None se Mongo indisponivel."""
    db = get_mongo_db()
    if db is None:
        return None
    return db["brand_assets"]


# Limites pra caber em doc do Cosmos DB (2MB por documento)
MAX_DIM = 1600
JPEG_QUALITY = 85


def _comprimir_imagem(raw_bytes: bytes) -> tuple[bytes, str]:
    """Comprime a imagem pra caber no Cosmos DB (max 2MB por doc).

    - Resize: max 1600px no lado maior
    - Format: JPEG quality 85
    - Converte RGBA/P pra RGB (necessario pra JPEG)

    Returns:
        (bytes comprimidos, mime_type sempre 'image/jpeg')
    """
    img = Image.open(io.BytesIO(raw_bytes))

    # RGBA ou P -> achatar em fundo branco (JPEG nao suporta alpha)
    if img.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # Resize proporcional se passa do limite
    w, h = img.size
    if max(w, h) > MAX_DIM:
        if w >= h:
            new_w = MAX_DIM
            new_h = int(h * MAX_DIM / w)
        else:
            new_h = MAX_DIM
            new_w = int(w * MAX_DIM / h)
        img = img.resize((new_w, new_h), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return buf.getvalue(), "image/jpeg"


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
    """Cria brand novo. Raises FileExistsError se ja existe."""
    return _salvar_brand(slug, data)


def atualizar_brand(slug: str, data: dict) -> dict | None:
    """Atualiza brand existente. Retorna None se nao encontrado."""
    if not carregar_brand(slug):
        return None
    data["slug"] = slug
    return _salvar_brand(slug, data, overwrite=True)


def deletar_brand_service(slug: str) -> bool:
    return _deletar_brand(slug)


def clonar_brand(slug_origem: str, slug_destino: str, nome_destino: str) -> dict:
    """Clona uma marca existente com novo slug e nome. Copia JSON + assets do Mongo."""
    import re

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

    # Clonar assets no Mongo (foto + refs + avatares)
    col = _get_assets_col()
    if col is not None:
        docs = list(col.find({"slug": slug_origem}, {"_id": 0}))
        for doc in docs:
            novo_doc = {**doc, "slug": slug_destino}
            col.update_one(
                {"slug": slug_destino, "nome": doc["nome"]},
                {"$set": novo_doc},
                upsert=True,
            )

    return {"slug": slug_destino, "nome": nome_destino, "mensagem": f"Marca '{nome_destino}' clonada de '{slug_origem}'"}


def salvar_foto_brand(slug: str, foto_data: str) -> dict:
    """Salva foto da marca no MongoDB. Comprime pra caber no doc (max 2MB)."""
    raw_b64 = foto_data.split(",")[1] if "," in foto_data else foto_data
    raw_bytes = b64.b64decode(raw_b64)

    comprimido, mime = _comprimir_imagem(raw_bytes)
    raw_b64 = b64.b64encode(comprimido).decode()
    data_uri = f"data:{mime};base64,{raw_b64}"

    col = _get_assets_col()
    if col is None:
        raise RuntimeError("MongoDB indisponivel — nao foi possivel salvar a foto")

    col.update_one(
        {"slug": slug, "nome": "__foto__"},
        {"$set": {"slug": slug, "nome": "__foto__", "data_uri": data_uri, "is_referencia": False}},
        upsert=True,
    )

    return {"slug": slug, "foto": data_uri}


def buscar_foto_brand(slug: str) -> dict:
    """Busca foto da marca no MongoDB."""
    col = _get_assets_col()
    if col is None:
        return {"foto": None}

    doc = col.find_one({"slug": slug, "nome": "__foto__"}, {"_id": 0})
    if doc and doc.get("data_uri"):
        return {"foto": doc["data_uri"]}
    return {"foto": None}


def buscar_foto_brand_b64(slug: str) -> str | None:
    """Retorna foto como data URI base64 (uso interno)."""
    result = buscar_foto_brand(slug)
    return result.get("foto")


def listar_assets(slug: str) -> dict:
    """Lista assets da marca no MongoDB.

    Cada item retorna o campo `pool` detectado pelo prefixo do nome:
    'com_avatar' | 'sem_avatar' | None (se eh avatar/foto).
    """
    items = []

    col = _get_assets_col()
    if col is None:
        return {"assets": [], "total": 0}

    docs = list(col.find({"slug": slug}, {"_id": 0}))
    for doc in docs:
        nome = doc.get("nome", "")
        if nome == "__foto__":
            continue
        items.append({
            "nome": nome,
            "arquivo": f"{nome}.jpg",
            "preview": doc.get("data_uri", ""),
            "is_referencia": doc.get("is_referencia", nome.startswith("ref_")),
            "pool": detectar_pool(nome),
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


def upload_asset(slug: str, nome: str, imagem: str, pool: str | None = None) -> dict:
    """Salva asset no MongoDB.

    Args:
        slug: brand slug
        nome: nome do asset. Se `pool` for passado, o nome eh automaticamente
              prefixado com ref_ca_ ou ref_sa_ (substituindo prefixo existente).
        imagem: base64 data URI
        pool: 'com_avatar' | 'sem_avatar' | None. Se None, usa o `nome` como veio
              (compat com upload de avatar/foto que nao eh ref).

    Raises:
        ValueError: se pool invalido
        RuntimeError: se Mongo indisponivel
    """
    if pool is not None:
        if pool not in VALID_POOLS:
            raise ValueError(f"pool invalido: {pool}. Use 'com_avatar' ou 'sem_avatar'")
        nome = _aplicar_prefixo_pool(nome, pool)

    raw_b64 = imagem.split(",")[1] if "," in imagem else imagem
    raw_bytes = b64.b64decode(raw_b64)

    # Comprimir pra caber no Cosmos DB (max 2MB por doc)
    comprimido, mime = _comprimir_imagem(raw_bytes)
    raw_b64 = b64.b64encode(comprimido).decode()
    data_uri = f"data:{mime};base64,{raw_b64}"

    col = _get_assets_col()
    if col is None:
        raise RuntimeError("MongoDB indisponivel — nao foi possivel salvar o asset")

    col.update_one(
        {"slug": slug, "nome": nome},
        {"$set": {
            "slug": slug,
            "nome": nome,
            "data_uri": data_uri,
            "is_referencia": nome.startswith("ref_"),
        }},
        upsert=True,
    )

    return {"nome": nome, "arquivo": f"{nome}.jpg", "pool": detectar_pool(nome)}


def deletar_asset(slug: str, nome: str) -> dict | None:
    """Deleta asset do MongoDB."""
    col = _get_assets_col()
    if col is None:
        return None

    result = col.delete_one({"slug": slug, "nome": nome})
    if result.deleted_count > 0:
        return {"deletado": nome}
    return None


def _extrair_bytes_data_uri(data_uri: str) -> tuple[bytes, str]:
    """Extrai bytes e mime type de um data URI base64.

    Returns:
        (bytes, mime_type)
    """
    if not data_uri:
        return b"", "image/png"

    mime = "image/png"
    if data_uri.startswith("data:"):
        header, _, raw = data_uri.partition(",")
        if ";" in header:
            mime = header.split(":", 1)[1].split(";", 1)[0]
    else:
        raw = data_uri

    return b64.b64decode(raw), mime


def buscar_foto_brand_bytes(slug: str) -> tuple[bytes, str] | None:
    """Busca a foto da marca como bytes + mime type.

    Returns:
        (bytes, mime) ou None se nao encontrada.
    """
    col = _get_assets_col()
    if col is None:
        return None
    doc = col.find_one({"slug": slug, "nome": "__foto__"}, {"_id": 0, "data_uri": 1})
    if not doc or not doc.get("data_uri"):
        return None
    return _extrair_bytes_data_uri(doc["data_uri"])


def buscar_asset_bytes(slug: str, nome: str) -> tuple[bytes, str] | None:
    """Busca um asset especifico da marca como bytes + mime type.

    Returns:
        (bytes, mime) ou None se nao encontrado.
    """
    col = _get_assets_col()
    if col is None:
        return None
    doc = col.find_one({"slug": slug, "nome": nome}, {"_id": 0, "data_uri": 1})
    if not doc or not doc.get("data_uri"):
        return None
    return _extrair_bytes_data_uri(doc["data_uri"])
