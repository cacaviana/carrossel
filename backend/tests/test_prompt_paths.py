"""Testa que todos os agentes encontram seus arquivos .md de prompt."""
from pathlib import Path


AGENTS_DIR = Path(__file__).resolve().parent.parent / "agents"
PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "agents"


def test_strategist_md_exists():
    p = AGENTS_DIR / "strategist.md"
    fallback = PROMPTS_DIR / "strategist.md"
    assert p.exists() or fallback.exists(), f"strategist.md nao encontrado em {p} nem {fallback}"


def test_copywriter_md_exists():
    p = AGENTS_DIR / "copywriter.md"
    fallback = PROMPTS_DIR / "copywriter.md"
    assert p.exists() or fallback.exists()


def test_hook_specialist_md_exists():
    p = AGENTS_DIR / "hook-specialist.md"
    fallback = PROMPTS_DIR / "hook-specialist.md"
    assert p.exists() or fallback.exists()


def test_art_director_md_exists():
    p = AGENTS_DIR / "art-director.md"
    fallback = PROMPTS_DIR / "art-director.md"
    assert p.exists() or fallback.exists()


def test_content_critic_md_exists():
    p = AGENTS_DIR / "content-critic.md"
    fallback = PROMPTS_DIR / "content-critic.md"
    assert p.exists() or fallback.exists()


def test_prompt_files_are_not_empty():
    """Verifica que os prompts tem conteudo real (> 100 chars)."""
    for name in ["strategist", "copywriter", "hook-specialist", "art-director", "content-critic"]:
        for base in [AGENTS_DIR, PROMPTS_DIR]:
            p = base / f"{name}.md"
            if p.exists():
                content = p.read_text(encoding="utf-8")
                assert len(content) > 100, f"{p} esta vazio ou muito curto ({len(content)} chars)"
                break
