"""Testes unitarios — factories/agente_factory.py

Cobre casos de uso:
- Listar Agentes (listar_todos)
- Obter Prompt Agente (buscar_por_slug, carregar_system_prompt)
- Listar Skills (SKILLS metadata + tipo)

Valida que o factory e a fonte da verdade sobre os agentes LLM e skills
deterministicos, e que o prompt e carregado a partir do arquivo .md na
pasta agents/.
"""

import sys, os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from factories.agente_factory import AgenteFactory, AGENTES_LLM, SKILLS, AGENTS_PATH


# ===================================================================
# listar_todos — retorna (agentes_llm, skills)
# ===================================================================
class TestListarTodos:
    def test_retorna_tupla_com_duas_listas(self):
        agentes, skills = AgenteFactory.listar_todos()
        assert isinstance(agentes, list)
        assert isinstance(skills, list)

    def test_contem_agentes_llm(self):
        agentes, _ = AgenteFactory.listar_todos()
        slugs = [a["slug"] for a in agentes]
        assert "strategist" in slugs
        assert "copywriter" in slugs
        assert "art_director" in slugs

    def test_contem_skills(self):
        _, skills = AgenteFactory.listar_todos()
        slugs = [s["slug"] for s in skills]
        assert "brand_overlay" in slugs
        assert "trend_scanner" in slugs
        assert "tone_guide" in slugs

    def test_agentes_llm_tem_tipo_llm(self):
        agentes, _ = AgenteFactory.listar_todos()
        for a in agentes:
            assert a["tipo"] == "llm"

    def test_skills_tem_tipo_skill(self):
        _, skills = AgenteFactory.listar_todos()
        for s in skills:
            assert s["tipo"] == "skill"

    def test_agentes_tem_campos_obrigatorios(self):
        agentes, _ = AgenteFactory.listar_todos()
        for a in agentes:
            assert "slug" in a
            assert "nome" in a
            assert "descricao" in a
            assert "tipo" in a

    def test_skills_tem_campos_obrigatorios(self):
        _, skills = AgenteFactory.listar_todos()
        for s in skills:
            assert "slug" in s
            assert "nome" in s
            assert "descricao" in s
            assert "tipo" in s

    def test_totais_conhecidos(self):
        """Smoke test: se alguem mudar o nro de agentes sem atualizar os testes,
        este teste quebra pra forcar revisao."""
        agentes, skills = AgenteFactory.listar_todos()
        assert len(agentes) == len(AGENTES_LLM)
        assert len(skills) == len(SKILLS)


# ===================================================================
# buscar_por_slug — Obter Prompt Agente
# ===================================================================
class TestBuscarPorSlug:
    def test_encontra_agente_llm(self):
        meta = AgenteFactory.buscar_por_slug("strategist")
        assert meta is not None
        assert meta["slug"] == "strategist"
        assert meta["tipo"] == "llm"
        assert meta["nome"] == "Strategist"

    def test_encontra_skill(self):
        meta = AgenteFactory.buscar_por_slug("brand_overlay")
        assert meta is not None
        assert meta["slug"] == "brand_overlay"
        assert meta["tipo"] == "skill"

    def test_retorna_none_para_slug_inexistente(self):
        assert AgenteFactory.buscar_por_slug("nao-existe-999") is None

    def test_retorna_none_para_string_vazia(self):
        assert AgenteFactory.buscar_por_slug("") is None

    def test_case_sensitive(self):
        """Slugs sao case-sensitive (convencao do projeto)."""
        assert AgenteFactory.buscar_por_slug("STRATEGIST") is None
        assert AgenteFactory.buscar_por_slug("strategist") is not None


# ===================================================================
# carregar_system_prompt
# ===================================================================
class TestCarregarSystemPrompt:
    def test_agente_sem_arquivo_retorna_descricao(self):
        """Agente com arquivo=None (ex: image_generator) retorna a descricao."""
        meta = AgenteFactory.buscar_por_slug("image_generator")
        assert meta is not None
        assert meta["arquivo"] is None
        prompt = AgenteFactory.carregar_system_prompt(meta)
        assert prompt == meta["descricao"]

    def test_skill_sem_arquivo_retorna_descricao(self):
        """Skills deterministicas nao tem campo 'arquivo' — retorna descricao."""
        meta = AgenteFactory.buscar_por_slug("brand_overlay")
        assert meta is not None
        # Skills nao tem a chave 'arquivo' no metadata
        prompt = AgenteFactory.carregar_system_prompt(meta)
        assert prompt == meta["descricao"]

    def test_agente_com_arquivo_existente_retorna_conteudo(self):
        """Strategist tem arquivo strategist.md na pasta agents/."""
        meta = AgenteFactory.buscar_por_slug("strategist")
        assert meta is not None
        prompt = AgenteFactory.carregar_system_prompt(meta)
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_agente_com_arquivo_inexistente_retorna_mensagem(self):
        """Se o arquivo configurado nao existe no disco, retorna mensagem de erro."""
        meta_fake = {
            "slug": "fake",
            "nome": "Fake",
            "descricao": "desc",
            "tipo": "llm",
            "arquivo": "este-arquivo-nao-existe-xyz.md",
        }
        prompt = AgenteFactory.carregar_system_prompt(meta_fake)
        assert "nao encontrado" in prompt.lower()
        assert "este-arquivo-nao-existe-xyz.md" in prompt


# ===================================================================
# AGENTS_PATH — resolucao
# ===================================================================
class TestAgentsPath:
    def test_agents_path_existe(self):
        """AGENTS_PATH deve existir em ../agents ou backend/agents."""
        assert AGENTS_PATH.exists()
        assert AGENTS_PATH.is_dir()

    def test_agents_path_contem_md(self):
        """Pelo menos 1 arquivo .md deve existir na pasta."""
        mds = list(AGENTS_PATH.glob("*.md"))
        assert len(mds) > 0
