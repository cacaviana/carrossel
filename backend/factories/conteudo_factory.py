"""Factory de conteúdo — monta prompts e cria objetos."""

from pathlib import Path

# Funciona local (agents/ na raiz do projeto) e em produção (agents/ copiado para backend/)
_BASE = Path(__file__).parent.parent
SKILL_PATH = _BASE / "agents" / "anti-bel-pesce.md"
if not SKILL_PATH.exists():
    SKILL_PATH = _BASE.parent / "agents" / "anti-bel-pesce.md"

DISCIPLINAS = {
    "D1": "D1 — Linguagens",
    "D2": "D2 — ETL",
    "D3": "D3 — Fundamentos ML",
    "D4": "D4 — Modelagem Preditiva",
    "D5": "D5 — Deep Learning",
    "D6": "D6 — NLP",
    "D7": "D7 — IA Generativa",
    "D8": "D8 — Cloud",
    "D9": "D9 — ML em Producao",
}


def build_system_prompt() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


TIPO_INSTRUCOES = {
    "texto": (
        "ESTILO: Carrossel de TEXTO TECNICO. "
        "Slides com headlines, bullets, codigo real. "
        "Foco em conteudo escrito claro e didatico. "
        "REGRA: O conteudo DEVE seguir EXATAMENTE o tema que o usuario escreveu."
    ),
    "visual": (
        "ESTILO: Carrossel VISUAL com ilustracoes e diagramas. "
        "REGRA: O conteudo DEVE seguir EXATAMENTE o tema que o usuario escreveu. "
        "Cada slide DEVE incluir um campo 'illustration_description' com uma descricao DETALHADA "
        "do diagrama, fluxograma, grafico ou ilustracao que explica o TEMA DO USUARIO. "
        "O texto do slide deve ser CURTO (1-2 linhas) — a ilustracao e o foco principal. "
        "Use o campo 'illustration_description' em TODOS os slides de conteudo."
    ),
    "infografico": (
        "ESTILO: INFOGRAFICO unico — 1 slide denso e visual. "
        "REGRA CRITICA: O infografico DEVE ser sobre EXATAMENTE o tema que o usuario escreveu. "
        "NAO invente outro tema. Use as palavras, conceitos e dados do texto do usuario. "
        "Crie um slide UNICO tipo 'infographic' com: "
        "titulo que reflita o tema do usuario, "
        "campo 'illustration_description' descrevendo o layout visual do infografico "
        "com diagramas, fluxos, metricas e secoes que explicam o tema do usuario. "
        "Inclua 'bullets' com os dados/pontos-chave extraidos do texto do usuario. "
        "O infografico deve ser RICO visualmente — numeros grandes, cores, secoes bem definidas. "
        "NAO e carrossel, e UM UNICO SLIDE de alto impacto visual."
    ),
}


def build_user_prompt(
    disciplina: str | None,
    tecnologia: str | None,
    tema_custom: str | None,
    texto_livre: str | None,
    total_slides: int = 10,
    tipo_carrossel: str = "texto",
) -> str:
    if texto_livre:
        prompt = (
            "O usuário enviou o seguinte texto para ser transformado em carrossel LinkedIn:\n\n"
            f"---\n{texto_livre}\n---\n\n"
            "Transforme este conteúdo em um carrossel LinkedIn técnico para Carlos Viana / IT Valley School."
        )
    else:
        disc_nome = DISCIPLINAS.get(disciplina, disciplina)
        prompt = f"Crie um carrossel LinkedIn sobre {tecnologia} da disciplina {disc_nome}."
        if tema_custom:
            prompt += f"\n\nTema específico: {tema_custom}"

    # Tipo de carrossel
    tipo_inst = TIPO_INSTRUCOES.get(tipo_carrossel, TIPO_INSTRUCOES["texto"])
    prompt += f"\n\n{tipo_inst}"

    if tipo_carrossel == "infografico":
        prompt += "\n\nGere EXATAMENTE 1 slide (infografico unico)."
    else:
        prompt += f"\n\nGere EXATAMENTE {total_slides} slides (formato de {total_slides} slides)."

    prompt += (
        "\n\nIMPORTANTE: Inclua o campo 'tipo_layout' em TODOS os slides. "
        "Valores: 'texto' (paragrafo/headline), 'lista' (bullets), 'comparativo' (X vs Y), 'dados' (numeros em destaque)."
    )

    prompt += "\n\nRetorne SOMENTE o JSON no formato especificado, sem texto antes ou depois."

    if tipo_carrossel in ("visual", "infografico"):
        prompt += (
            "\n\nIMPORTANTE: Inclua o campo 'illustration_description' em cada slide que deve ter ilustracao. "
            "Este campo sera usado pelo Gemini para gerar a imagem. Seja DETALHADO na descricao visual."
        )

    return prompt
