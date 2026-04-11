"""Remove campos deprecated dos brand profiles (Fase 7).

Campos removidos:
    elementos.badge_topo
    elementos.badge_topo_cor
    elementos.rodape_nome
    elementos.rodape_instituicao
    elementos.rodape_extra
    visual.badges
    visual.rodape
    visual.slide_codigo
    visual.estilo_elemento
    visual.posicionamento_elemento
    modo_geracao
    overrides

Motivo: esses campos sao atribuicoes de FORMATO/CTA, nao de marca.
A Fase 5/6 moveu essas regras pros modulos prompt_modules/ e
pra config de formato (configs/formatos.json).

Rodar uma vez:
    python backend/scripts/limpar_brand_deprecated.py

Por padrao, faz dry-run. Pra aplicar, use --apply.
"""

import argparse
import sys
from pathlib import Path

BACKEND = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND))

from dotenv import load_dotenv
load_dotenv(BACKEND / ".env")

from data.connections.mongo_connection import get_mongo_db  # noqa: E402


DEPRECATED_TOP = ("modo_geracao", "overrides")
DEPRECATED_ELEMENTOS = (
    "badge_topo", "badge_topo_cor",
    "rodape_nome", "rodape_instituicao", "rodape_extra",
)
DEPRECATED_VISUAL = (
    "badges", "rodape", "slide_codigo",
    "estilo_elemento", "posicionamento_elemento",
)


def _limpar_dict(brand: dict) -> tuple[dict, list[str]]:
    """Retorna (brand_limpo, lista_de_chaves_removidas)."""
    removidas = []
    clean = {**brand}

    for key in DEPRECATED_TOP:
        if key in clean:
            del clean[key]
            removidas.append(key)

    elementos = clean.get("elementos")
    if isinstance(elementos, dict):
        new_el = {k: v for k, v in elementos.items() if k not in DEPRECATED_ELEMENTOS}
        for k in DEPRECATED_ELEMENTOS:
            if k in elementos:
                removidas.append(f"elementos.{k}")
        if new_el:
            clean["elementos"] = new_el
        else:
            del clean["elementos"]

    visual = clean.get("visual")
    if isinstance(visual, dict):
        new_v = {k: v for k, v in visual.items() if k not in DEPRECATED_VISUAL}
        for k in DEPRECATED_VISUAL:
            if k in visual:
                removidas.append(f"visual.{k}")
        clean["visual"] = new_v

    return clean, removidas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Aplicar (senao, so dry run)")
    args = parser.parse_args()

    # Importar DEPOIS de load_dotenv pra .env estar carregado
    from services.brand_prompt_builder import listar_brands, carregar_brand, salvar_brand

    print(f"=== Limpar campos deprecated ({'APPLY' if args.apply else 'DRY RUN'}) ===\n")

    brands = listar_brands()
    if not brands:
        print("[X] Nenhuma marca encontrada")
        return

    total_limpo = 0
    for b in brands:
        slug = b["slug"]
        brand = carregar_brand(slug)
        if not brand:
            continue
        clean, removidas = _limpar_dict(brand)
        if not removidas:
            print(f"[SKIP] {slug} — ja limpo")
            continue

        print(f"[{slug}] remover: {', '.join(removidas)}")
        if args.apply:
            salvar_brand(slug, clean, overwrite=True)
            total_limpo += 1

    print()
    if args.apply:
        print(f"Aplicado em {total_limpo} marca(s).")
    else:
        print("Dry run — rode com --apply pra efetivar.")


if __name__ == "__main__":
    main()
