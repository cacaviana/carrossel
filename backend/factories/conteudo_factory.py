"""Factory de conteúdo — monta prompts e cria objetos."""

from pathlib import Path

SKILL_PATH = Path(__file__).parent.parent.parent / "agents" / "anti-bel-pesce.md"

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


def build_user_prompt(
    disciplina: str | None,
    tecnologia: str | None,
    tema_custom: str | None,
    texto_livre: str | None,
    total_slides: int = 10,
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

    prompt += f"\n\nGere EXATAMENTE {total_slides} slides (formato de {total_slides} slides)."
    prompt += "\n\nRetorne SOMENTE o JSON no formato especificado, sem texto antes ou depois."
    return prompt
