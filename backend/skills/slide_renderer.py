"""Renderiza slides via HTML/CSS + Playwright screenshot.

Segue o design system nano-banana-carrossel.md:
- Fundo: #0A0A0F com background Gemini
- Texto: Outfit font, hierarquia de cores
- Destaques: roxo #A78BFA, verde #34D399, amber #FBBF24
- Rodape: foto criador (circulo) + DESLIZA + paginacao
- Codigo: janela macOS com syntax highlight verde
"""
import asyncio
import base64
import io
import os
from pathlib import Path

# Assets directory
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

# Foto do criador (fallback)
FOTO_CRIADOR_PATH = ASSETS_DIR / "foto_criador.jpg"


def _load_foto_criador() -> str | None:
    if FOTO_CRIADOR_PATH.exists():
        import base64 as b64mod
        data = FOTO_CRIADOR_PATH.read_bytes()
        return f"data:image/jpeg;base64,{b64mod.b64encode(data).decode()}"
    return None

DIMS = {
    "carrossel": (1080, 1350),
    "post_unico": (1080, 1080),
    "thumbnail_youtube": (1280, 720),
}

# CSS compartilhado - usa variaveis CSS preenchidas pelo design system
BASE_CSS = """
@import url('{google_fonts}');

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    width: {width}px;
    height: {height}px;
    background: {cor_fundo};
    color: {cor_texto_principal};
    font-family: '{fonte_titulo}', sans-serif;
    overflow: hidden;
    position: relative;
}

.bg-image {
    position: absolute;
    inset: 0;
    opacity: 0.35;
    background-size: cover;
    background-position: center;
    z-index: 0;
}

.gradient-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, {cor_gradiente_de} 0%, transparent 40%, {cor_gradiente_ate} 100%);
    z-index: 1;
}

.content {
    position: relative;
    z-index: 2;
    height: 100%;
    padding: 60px 70px;
    display: flex;
    flex-direction: column;
}

/* Glows */
.glow {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    z-index: 1;
    pointer-events: none;
}
.glow-purple { background: #A78BFA; opacity: 0.08; }
.glow-green { background: #34D399; opacity: 0.06; }

/* Typography */
.text-white { color: #FFFFFF; }
.text-secondary { color: #9896A3; }
.text-muted { color: #5A5A66; }
.text-purple { color: #A78BFA; }
.text-green { color: #34D399; }
.text-amber { color: #FBBF24; }
.text-red { color: #F87171; }

.font-light { font-weight: 300; }
.font-regular { font-weight: 400; }
.font-semibold { font-weight: 600; }
.font-mono { font-family: 'JetBrains Mono', monospace; }

/* Badge */
.badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.badge-green { border: 1px solid #34D399; background: rgba(52,211,153,0.1); color: #34D399; }
.badge-purple { border: 1px solid rgba(167,139,250,0.3); background: rgba(167,139,250,0.1); color: #A78BFA; }
.badge-red { border: 1px solid rgba(248,113,113,0.15); background: rgba(248,113,113,0.09); color: #F87171; }

/* Card */
.card {
    background: #12121A;
    border: 1px solid rgba(167,139,250,0.15);
    border-radius: 16px;
    padding: 40px;
    flex: 1;
}

/* Terminal macOS */
.terminal {
    border: 1px solid #1E1E35;
    border-radius: 10px;
    overflow: hidden;
    flex: 1;
}
.terminal-bar {
    height: 36px;
    background: #1a1a2a;
    display: flex;
    align-items: center;
    padding: 0 16px;
    gap: 8px;
}
.terminal-dot { width: 12px; height: 12px; border-radius: 50%; }
.dot-red { background: #FF5F57; }
.dot-yellow { background: #FEBC2E; }
.dot-green { background: #28C840; }
.terminal-file {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #9896A3;
    margin-left: auto;
    margin-right: auto;
}
.terminal-body {
    background: #0D0D18;
    padding: 28px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 16px;
    color: #34D399;
    line-height: 1.6;
    white-space: pre-wrap;
    overflow: hidden;
}

/* Footer */
.footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 24px;
    margin-top: auto;
}
.footer-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
.avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: 2px solid #A78BFA;
    background: #1a1a2a;
    object-fit: cover;
}
.avatar-placeholder {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: 2px solid #A78BFA;
    background: linear-gradient(135deg, #A78BFA, #6D28D9);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 600;
    color: white;
}
.footer-name { font-size: 14px; font-weight: 500; }
.footer-nav { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #A78BFA; }
.footer-pag { font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #5A5A66; }

/* Separator */
.separator { width: 60px; height: 3px; background: #A78BFA; border-radius: 2px; margin: 20px 0; }
"""


def _apply_ds_to_css(css: str, ds: dict) -> str:
    """Substitui variáveis no CSS com valores do design system."""
    cores = ds.get("cores", {})
    fontes = ds.get("fontes", {})
    replacements = {
        "{google_fonts}": fontes.get("google_fonts", ""),
        "{cor_fundo}": cores.get("fundo", "#0A0A0F"),
        "{cor_gradiente_de}": cores.get("gradiente_de", "#1a0a2e"),
        "{cor_gradiente_ate}": cores.get("gradiente_ate", "#0a1628"),
        "{cor_texto_principal}": cores.get("texto_principal", "#FFFFFF"),
        "{fonte_titulo}": fontes.get("titulo", "Outfit"),
    }
    for key, val in replacements.items():
        css = css.replace(key, val)
    # Substituir cores restantes hardcoded
    color_map = {
        "#0A0A0F": cores.get("fundo", "#0A0A0F"),
        "#12121A": cores.get("card", "#12121A"),
        "#9896A3": cores.get("texto_secundario", "#9896A3"),
        "#5A5A66": cores.get("texto_muted", "#5A5A66"),
        "#A78BFA": cores.get("acento_principal", "#A78BFA"),
        "#34D399": cores.get("acento_secundario", "#34D399"),
        "#FBBF24": cores.get("acento_terciario", "#FBBF24"),
        "#F87171": cores.get("acento_negativo", "#F87171"),
        "#1a1a2a": cores.get("terminal_barra", "#1a1a2a"),
        "#0D0D18": cores.get("terminal_corpo", "#0D0D18"),
        "#1E1E35": cores.get("terminal_borda", "#1E1E35"),
    }
    for old, new in color_map.items():
        css = css.replace(old, new)
    # Substituir fontes
    css = css.replace("'Outfit'", f"'{fontes.get('titulo', 'Outfit')}'")
    css = css.replace("'JetBrains Mono'", f"'{fontes.get('codigo', 'JetBrains Mono')}'")
    return css


def _build_slide_html(
    slide: dict,
    slide_index: int,
    total_slides: int,
    background_b64: str | None = None,
    formato: str = "carrossel",
    foto_criador: str | None = None,
    design_system: dict | None = None,
) -> str:
    from skills.design_system_loader import buscar_default
    ds = design_system or buscar_default()
    elementos = ds.get("elementos", {})

    width, height = DIMS.get(formato, DIMS["carrossel"])
    css = BASE_CSS.replace("{width}", str(width)).replace("{height}", str(height))
    css = _apply_ds_to_css(css, ds)

    tipo = slide.get("tipo", "conteudo")
    titulo = slide.get("titulo", "")
    corpo = slide.get("corpo", "")

    # Foto do criador: usar passada ou fallback do assets
    if not foto_criador:
        foto_criador = _load_foto_criador()

    # Background image
    bg_style = ""
    if background_b64:
        bg_data = background_b64 if background_b64.startswith("data:") else f"data:image/png;base64,{background_b64}"
        bg_style = f"background-image: url('{bg_data}');"

    # Textos da marca
    badge_topo = elementos.get("badge_topo", "Carlos Viana")
    rodape_nome = elementos.get("rodape_nome", "Carlos Viana")
    cta_texto = elementos.get("cta_texto", "Siga @carlosviana_ai")
    rodape_extra = elementos.get("rodape_extra", "")
    rodape_instituicao = elementos.get("rodape_instituicao", "")

    # Avatar
    initials = "".join(w[0] for w in rodape_nome.split()[:2]).upper() if rodape_nome else "CV"
    avatar_html = f'<div class="avatar-placeholder">{initials}</div>'
    if foto_criador:
        foto_data = foto_criador if foto_criador.startswith("data:") else f"data:image/jpeg;base64,{foto_criador}"
        avatar_html = f'<img class="avatar" src="{foto_data}" alt="Carlos Viana">'

    # Footer (todos os slides)
    footer_nav = f'<span class="footer-nav">DESLIZA →</span>' if slide_index < total_slides else ''
    footer_html = f"""
    <div class="footer">
        <div class="footer-left">
            {avatar_html}
            <span class="footer-name text-white">{_escape(rodape_nome)}</span>
        </div>
        {footer_nav}
        <span class="footer-pag">{slide_index:02d} / {total_slides:02d}</span>
    </div>
    """

    # Corpo do slide por tipo
    if tipo == "capa":
        body_html = _html_capa(titulo, corpo, badge_topo)
    elif tipo in ("codigo", "code"):
        body_html = _html_codigo(titulo, corpo)
    elif tipo == "cta":
        body_html = _html_cta(titulo, corpo, cta_texto, rodape_nome, rodape_instituicao, rodape_extra)
    elif tipo == "dados":
        body_html = _html_dados(titulo, corpo)
    else:
        body_html = _html_conteudo(titulo, corpo)

    # Glows
    glows = """
    <div class="glow glow-purple" style="width:400px;height:400px;top:-100px;right:-100px;"></div>
    <div class="glow glow-green" style="width:300px;height:300px;bottom:-50px;left:-80px;"></div>
    """

    return f"""<!DOCTYPE html>
<html><head><style>{css}</style></head>
<body>
    <div class="bg-image" style="{bg_style}"></div>
    <div class="gradient-overlay"></div>
    {glows}
    <div class="content">
        {body_html}
        {footer_html}
    </div>
</body></html>"""


def _html_capa(titulo, corpo, badge_topo="Carlos Viana"):
    corpo_html = f'<p style="font-size:24px;line-height:1.6;max-width:80%;" class="text-secondary font-light">{_escape(corpo)}</p>' if corpo else ''
    return f"""
    <div style="margin-bottom:20px;">
        <span class="badge badge-green">{_escape(badge_topo)}</span>
    </div>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:24px;">
        <h1 style="font-size:52px;line-height:1.15;font-weight:600;max-width:90%;">{_escape(titulo)}</h1>
        {corpo_html}
    </div>
    """


def _html_conteudo(titulo, corpo):
    corpo_lines = corpo.replace("\\n", "\n").split("\n") if corpo else []
    corpo_html = "".join(f'<p style="margin-bottom:12px;">{_escape(line)}</p>' for line in corpo_lines if line.strip())
    return f"""
    <div class="card" style="display:flex;flex-direction:column;gap:20px;">
        <h2 style="font-size:36px;font-weight:600;line-height:1.2;">{_escape(titulo)}</h2>
        <div class="separator"></div>
        <div style="font-size:22px;line-height:1.6;color:#9896A3;font-weight:300;">
            {corpo_html}
        </div>
    </div>
    """


def _html_codigo(titulo, corpo):
    code_escaped = _escape(corpo).replace("\\n", "\n") if corpo else ""
    return f"""
    <div style="margin-bottom:16px;">
        <span class="badge badge-green">CODIGO REAL</span>
    </div>
    <h2 style="font-size:30px;font-weight:600;margin-bottom:20px;">{_escape(titulo)}</h2>
    <div class="terminal">
        <div class="terminal-bar">
            <div class="terminal-dot dot-red"></div>
            <div class="terminal-dot dot-yellow"></div>
            <div class="terminal-dot dot-green"></div>
            <span class="terminal-file">agent.py</span>
        </div>
        <div class="terminal-body">{code_escaped}</div>
    </div>
    """


def _html_dados(titulo, corpo):
    corpo_lines = corpo.replace("\\n", "\n").split("\n") if corpo else []
    metrics_html = ""
    for line in corpo_lines:
        if ":" in line:
            label, value = line.split(":", 1)
            metrics_html += f"""
            <div style="background:rgba(167,139,250,0.08);border:1px solid rgba(167,139,250,0.2);border-radius:10px;padding:20px;text-align:center;">
                <div style="font-size:32px;font-weight:600;color:#FBBF24;font-family:'JetBrains Mono',monospace;">{_escape(value.strip())}</div>
                <div style="font-size:12px;color:#9896A3;font-family:'JetBrains Mono',monospace;text-transform:uppercase;margin-top:8px;">{_escape(label.strip())}</div>
            </div>
            """
        elif line.strip():
            metrics_html += f'<p style="font-size:20px;color:#9896A3;grid-column:1/-1;">{_escape(line)}</p>'

    return f"""
    <div class="card" style="display:flex;flex-direction:column;gap:20px;">
        <h2 style="font-size:34px;font-weight:600;">{_escape(titulo)}</h2>
        <div class="separator"></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;flex:1;">
            {metrics_html}
        </div>
    </div>
    """


def _html_cta(titulo, corpo, cta_texto="Siga @carlosviana_ai", nome="Carlos Viana", instituicao="IT Valley School", extra="Pos IA & ML"):
    corpo_html = f'<p style="font-size:22px;line-height:1.6;color:#9896A3;font-weight:300;">{_escape(corpo)}</p>' if corpo else ''
    footer_parts = [nome, instituicao, extra]
    footer_text = " — ".join(p for p in footer_parts if p)
    return f"""
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;gap:30px;">
        <div style="width:80px;height:3px;background:#A78BFA;border-radius:2px;"></div>
        <h2 style="font-size:42px;font-weight:600;line-height:1.2;max-width:80%;">{_escape(titulo)}</h2>
        {corpo_html}
        <div style="margin-top:20px;padding:16px 40px;background:#A78BFA;border-radius:30px;font-size:18px;font-weight:600;color:#0A0A0F;">
            {_escape(cta_texto)}
        </div>
        <p style="font-size:13px;color:#5A5A66;font-family:'JetBrains Mono',monospace;margin-top:40px;">
            {_escape(footer_text)}
        </p>
    </div>
    """


def _escape(text: str) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


async def renderizar_slide(
    slide: dict,
    slide_index: int,
    total_slides: int,
    background: str | None = None,
    formato: str = "carrossel",
    foto_criador: str | None = None,
    design_system: dict | None = None,
) -> str:
    """Renderiza um slide como screenshot base64 via Playwright subprocess."""
    results = await renderizar_todos([slide], background, formato, foto_criador, design_system)
    return results[0]["image_base64"] if results else ""


async def renderizar_todos(
    slides: list[dict],
    background: str | None = None,
    formato: str = "carrossel",
    foto_criador: str | None = None,
    design_system: dict | None = None,
) -> list[dict]:
    """Renderiza slides via subprocess Playwright (evita conflito de event loop no Windows)."""
    import asyncio
    import json
    import subprocess
    import sys
    import tempfile

    width, height = DIMS.get(formato, DIMS["carrossel"])
    total = len(slides)

    # Gerar HTML de cada slide
    htmls = []
    for i, slide in enumerate(slides):
        idx = slide.get("indice", i + 1)
        html = _build_slide_html(slide, idx, total, background, formato, foto_criador, design_system)
        htmls.append({"idx": idx, "titulo": slide.get("titulo", ""), "html": html})

    # Salvar job em arquivo temp
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump({"htmls": htmls, "width": width, "height": height}, f, ensure_ascii=False)
        job_path = f.name

    # Rodar subprocess via run_in_executor (Windows compat)
    script = str(Path(__file__).resolve().parent / "_pw_worker.py")

    def _run_worker():
        import subprocess as sp
        proc = sp.run(
            [sys.executable, script, job_path],
            capture_output=True, timeout=300,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Playwright worker falhou: {proc.stderr.decode('utf-8', errors='replace')[-500:]}")
        # Worker escreve resultado em arquivo
        output_path = job_path.replace(".json", "_output.json")
        with open(output_path, "r", encoding="utf-8") as f:
            result = json.load(f)
        os.unlink(output_path)
        return result

    result = await asyncio.get_event_loop().run_in_executor(None, _run_worker)
    os.unlink(job_path)
    return result
