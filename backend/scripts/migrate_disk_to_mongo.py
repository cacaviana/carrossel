"""Migra assets de brand (logo, avatares, refs) do disco local pro MongoDB.

Roda uma vez. Idempotente — so sobe o que nao ja existe no Mongo.
Necessario antes de deploy Azure (disco efemero).

Uso:
    python backend/scripts/migrate_disk_to_mongo.py
    python backend/scripts/migrate_disk_to_mongo.py --slug jennie  # so uma marca
    python backend/scripts/migrate_disk_to_mongo.py --force         # sobrescreve
"""

import argparse
import base64 as b64
import sys
from pathlib import Path

# Adicionar backend ao path pra imports funcionarem
BACKEND = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND))

from dotenv import load_dotenv
load_dotenv(BACKEND / ".env")

from data.connections.mongo_connection import get_mongo_db  # noqa: E402
from services.brand_service import _comprimir_imagem  # noqa: E402


ASSETS_ROOT = BACKEND / "assets"
FOTOS_DIR = ASSETS_ROOT / "fotos"
BRAND_ASSETS_DIR = ASSETS_ROOT / "brand-assets"

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")


def _encode_file(f: Path) -> str:
    """Le o arquivo, comprime e devolve data URI base64 (max 2MB pro Cosmos DB)."""
    raw_bytes = f.read_bytes()
    comprimido, mime = _comprimir_imagem(raw_bytes)
    data = b64.b64encode(comprimido).decode()
    return f"data:{mime};base64,{data}"


def migrate_fotos(col, slug_filter: str | None, force: bool) -> tuple[int, int]:
    """Migra logos da pasta fotos/ pro Mongo (nome='__foto__').

    Returns:
        (migradas, puladas)
    """
    if not FOTOS_DIR.exists():
        return (0, 0)

    migradas = 0
    puladas = 0
    for f in FOTOS_DIR.iterdir():
        if f.suffix.lower() not in IMAGE_EXTS:
            continue
        slug = f.stem
        if slug_filter and slug != slug_filter:
            continue

        if not force:
            exists = col.find_one({"slug": slug, "nome": "__foto__"}, {"_id": 1})
            if exists:
                print(f"  [SKIP foto] {slug}")
                puladas += 1
                continue

        data_uri = _encode_file(f)
        col.update_one(
            {"slug": slug, "nome": "__foto__"},
            {"$set": {
                "slug": slug,
                "nome": "__foto__",
                "data_uri": data_uri,
                "is_referencia": False,
            }},
            upsert=True,
        )
        print(f"  [OK foto] {slug}  ({f.name})")
        migradas += 1

    return (migradas, puladas)


def migrate_assets(col, slug_filter: str | None, force: bool) -> tuple[int, int, int]:
    """Migra assets (refs + avatares) de brand-assets/<slug>/ pro Mongo.

    Returns:
        (migradas, puladas, erros)
    """
    if not BRAND_ASSETS_DIR.exists():
        return (0, 0, 0)

    migradas = 0
    puladas = 0
    erros = 0
    for brand_dir in BRAND_ASSETS_DIR.iterdir():
        if not brand_dir.is_dir():
            continue
        slug = brand_dir.name
        if slug_filter and slug != slug_filter:
            continue

        print(f"\n[brand] {slug}")
        for f in sorted(brand_dir.iterdir()):
            if f.suffix.lower() not in IMAGE_EXTS:
                continue

            # Pular arquivos obviamente corrompidos (menores que 1KB)
            if f.stat().st_size < 1024:
                print(f"  [SKIP corrompido <1KB] {f.name}")
                puladas += 1
                continue

            nome = f.stem

            # So migra se tem prefixo conhecido: ref_, avatar_, ou mascote_ (doceria)
            # Arquivos orfaos (sem prefixo) nao aparecem na UI e ocupam espaco atoa
            if not (nome.startswith("ref_") or nome.startswith("avatar_") or nome.startswith("mascote_") or nome.startswith("carlos_")):
                print(f"  [SKIP orfao sem prefixo] {nome}")
                puladas += 1
                continue

            if not force:
                exists = col.find_one({"slug": slug, "nome": nome}, {"_id": 1})
                if exists:
                    print(f"  [SKIP] {nome}")
                    puladas += 1
                    continue

            try:
                data_uri = _encode_file(f)
            except Exception as e:
                print(f"  [ERRO {type(e).__name__}] {nome}: {e}")
                erros += 1
                continue

            is_ref = nome.startswith("ref_")
            try:
                col.update_one(
                    {"slug": slug, "nome": nome},
                    {"$set": {
                        "slug": slug,
                        "nome": nome,
                        "data_uri": data_uri,
                        "is_referencia": is_ref,
                    }},
                    upsert=True,
                )
            except Exception as e:
                print(f"  [ERRO Mongo] {nome}: {type(e).__name__}")
                erros += 1
                continue

            pool = ""
            if nome.startswith("ref_ca_"):
                pool = " (pool=com_avatar)"
            elif nome.startswith("ref_sa_"):
                pool = " (pool=sem_avatar)"
            elif nome.startswith("ref_"):
                pool = " (pool=com_avatar legado)"
            print(f"  [OK] {nome}{pool}")
            migradas += 1

    return (migradas, puladas, erros)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Migra so uma marca especifica")
    parser.add_argument("--force", action="store_true", help="Sobrescreve assets ja existentes no Mongo")
    args = parser.parse_args()

    db = get_mongo_db()
    if db is None:
        print("[X] MongoDB indisponivel — abortando")
        sys.exit(1)

    col = db["brand_assets"]
    print(f"=== Migracao disco -> Mongo (collection: brand_assets) ===")
    if args.slug:
        print(f"Slug filtro: {args.slug}")
    if args.force:
        print("Modo FORCE: vai sobrescrever assets ja existentes")
    print()

    print("--- Logos (assets/fotos/) ---")
    fotos_mig, fotos_skip = migrate_fotos(col, args.slug, args.force)

    print("\n--- Assets (assets/brand-assets/) ---")
    assets_mig, assets_skip, assets_err = migrate_assets(col, args.slug, args.force)

    print()
    print(f"=== Total ===")
    print(f"Logos:  {fotos_mig} migradas, {fotos_skip} puladas")
    print(f"Assets: {assets_mig} migrados, {assets_skip} pulados, {assets_err} erros")


if __name__ == "__main__":
    main()
