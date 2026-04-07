"""Testa que o strategist carrega o system prompt e ancora no tema."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_strategist_prompt_path_resolves():
    """O PROMPT_PATH deve encontrar o arquivo .md."""
    # Importar recarrega o modulo e resolve o path
    from agents import strategist
    assert strategist.PROMPT_PATH.exists(), (
        f"strategist.md nao encontrado em {strategist.PROMPT_PATH}"
    )


def test_strategist_prompt_has_content():
    from agents import strategist
    content = strategist.PROMPT_PATH.read_text(encoding="utf-8")
    assert len(content) > 100
    assert "Strategist" in content


def test_copywriter_prompt_path_resolves():
    from agents import copywriter
    assert copywriter.PROMPT_PATH.exists(), (
        f"copywriter.md nao encontrado em {copywriter.PROMPT_PATH}"
    )


def test_art_director_prompt_path_resolves():
    from agents import art_director
    assert art_director.PROMPT_PATH.exists(), (
        f"art-director.md nao encontrado em {art_director.PROMPT_PATH}"
    )


def test_hook_specialist_prompt_path_resolves():
    from agents import hook_specialist
    assert hook_specialist.PROMPT_PATH.exists(), (
        f"hook-specialist.md nao encontrado em {hook_specialist.PROMPT_PATH}"
    )


def test_content_critic_prompt_path_resolves():
    from agents import content_critic
    assert content_critic.PROMPT_PATH.exists(), (
        f"content-critic.md nao encontrado em {content_critic.PROMPT_PATH}"
    )
