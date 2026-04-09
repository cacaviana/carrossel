"""Seed: migra brands e formatos dos JSONs locais para MongoDB (Cosmos DB).

Uso: python scripts/seed_mongo.py
Executar de dentro de backend/ ou o script ajusta o path automaticamente.
"""

import json
import os
import sys
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))
os.chdir(Path(__file__).parent.parent)

from dotenv import load_dotenv
load_dotenv()

from data.connections.mongo_connection import get_mongo_db


def seed():
    db = get_mongo_db()
    if db is None:
        print("ERRO: MONGO_URL nao configurado no .env. Abortando.")
        return

    # Seed brands
    # Cosmos DB tem limite de 2MB por documento — remover campos pesados (base64)
    CAMPOS_PESADOS = {"_assets", "_fotoPreview", "_foto_base64"}
    brands_dir = Path("assets/design-systems")
    count_brands = 0
    if brands_dir.exists():
        for f in sorted(brands_dir.glob("*.json")):
            try:
                brand = json.loads(f.read_text(encoding="utf-8"))
                if "slug" not in brand:
                    brand["slug"] = f.stem
                brand_limpo = {k: v for k, v in brand.items() if k not in CAMPOS_PESADOS}
                db.brands.replace_one({"slug": brand_limpo["slug"]}, brand_limpo, upsert=True)
                count_brands += 1
                print(f"  Brand: {brand_limpo['slug']}")
            except Exception as e:
                print(f"  ERRO ao processar {f.name}: {e}")
    else:
        print(f"  Diretorio {brands_dir} nao encontrado, pulando brands.")

    # Seed formatos
    formatos_path = Path("configs/formatos.json")
    count_formatos = 0
    if formatos_path.exists():
        try:
            data = json.loads(formatos_path.read_text(encoding="utf-8"))
            for fmt in data.get("formatos", []):
                db.formatos.replace_one({"id": fmt["id"]}, fmt, upsert=True)
                count_formatos += 1
                print(f"  Formato: {fmt['id']}")
        except Exception as e:
            print(f"  ERRO ao processar formatos: {e}")
    else:
        print(f"  Arquivo {formatos_path} nao encontrado, pulando formatos.")

    print(f"\nSeed completo: {count_brands} brands, {count_formatos} formatos")


if __name__ == "__main__":
    seed()
