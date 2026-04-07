"""Carrega e gerencia design systems (marcas)."""
import json
from pathlib import Path

DS_DIR = Path(__file__).resolve().parent.parent / "assets" / "design-systems"
DS_DIR.mkdir(parents=True, exist_ok=True)

# Design system default (IT Valley) se nenhum for especificado
DEFAULT_SLUG = "itvalley"


def listar() -> list[dict]:
    """Lista todos os design systems disponíveis."""
    result = []
    for f in sorted(DS_DIR.glob("*.json")):
        try:
            ds = json.loads(f.read_text(encoding="utf-8"))
            result.append({"slug": ds["slug"], "nome": ds["nome"], "estilo": ds.get("estilo", "")})
        except Exception:
            continue
    return result


def buscar(slug: str) -> dict | None:
    """Busca um design system por slug."""
    path = DS_DIR / f"{slug}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def buscar_default() -> dict:
    """Retorna o design system default (IT Valley)."""
    ds = buscar(DEFAULT_SLUG)
    if not ds:
        # Fallback hardcoded minimo
        return {
            "slug": "itvalley", "nome": "IT Valley School",
            "cores": {
                "fundo": "#0A0A0F", "gradiente_de": "#1a0a2e", "gradiente_ate": "#0a1628",
                "card": "#12121A", "card_borda": "rgba(167,139,250,0.2)",
                "acento_principal": "#A78BFA", "acento_secundario": "#34D399",
                "acento_terciario": "#FBBF24", "acento_negativo": "#F87171",
                "texto_principal": "#FFFFFF", "texto_secundario": "#9896A3", "texto_muted": "#5A5A66",
                "terminal_barra": "#1a1a2a", "terminal_corpo": "#0D0D18", "terminal_borda": "#1E1E35",
            },
            "fontes": {"titulo": "Outfit", "corpo": "Outfit", "codigo": "JetBrains Mono",
                       "google_fonts": "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"},
            "pesos": {"titulo_light": 300, "titulo_bold": 600, "corpo": 400, "badge": 500},
            "elementos": {"badge_topo": "Carlos Viana", "badge_topo_cor": "verde",
                          "rodape_nome": "Carlos Viana", "rodape_instituicao": "IT Valley School",
                          "rodape_extra": "Pos IA & ML", "cta_texto": "Siga @carlosviana_ai",
                          "glow_cores": ["#A78BFA", "#34D399"], "glow_opacidade": 0.08},
        }
    return ds


def salvar(ds: dict) -> str:
    """Salva um design system. Retorna o slug."""
    slug = ds.get("slug", "").lower().replace(" ", "-")
    if not slug:
        slug = ds.get("nome", "unnamed").lower().replace(" ", "-")
        ds["slug"] = slug
    path = DS_DIR / f"{slug}.json"
    path.write_text(json.dumps(ds, ensure_ascii=False, indent=2), encoding="utf-8")
    return slug


def remover(slug: str) -> bool:
    path = DS_DIR / f"{slug}.json"
    if path.exists():
        path.unlink()
        return True
    return False
