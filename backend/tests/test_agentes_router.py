"""Testes unitarios — routers/agentes.py

Cobre:
- GET /agentes → Listar Agentes (inclui LLMs + Skills)
- GET /agentes/{slug} → Obter Prompt Agente (encontrado / 404)

O router e uma camada opaca: so delega pro AgenteFactory.
"""

import sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from main import app


client = TestClient(app, raise_server_exceptions=False)


class TestListarAgentesRota:
    def test_retorna_200_e_lista(self):
        resp = client.get("/api/agentes")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) > 0

    def test_inclui_agentes_llm_e_skills(self):
        resp = client.get("/api/agentes")
        body = resp.json()
        tipos = {item["tipo"] for item in body}
        assert "llm" in tipos
        assert "skill" in tipos

    def test_cada_item_tem_campos_esperados(self):
        resp = client.get("/api/agentes")
        body = resp.json()
        expected = {"slug", "nome", "descricao", "tipo", "conteudo"}
        for item in body:
            assert expected == set(item.keys())

    def test_conteudo_preenchido(self):
        """Conteudo nao pode ser vazio — ou carrega arquivo ou devolve descricao."""
        resp = client.get("/api/agentes")
        for item in resp.json():
            assert item["conteudo"] != ""


class TestBuscarAgenteRota:
    def test_slug_existente_retorna_200(self):
        resp = client.get("/api/agentes/strategist")
        assert resp.status_code == 200
        body = resp.json()
        assert body["slug"] == "strategist"
        assert body["tipo"] == "llm"

    def test_slug_skill_retorna_200(self):
        resp = client.get("/api/agentes/trend_scanner")
        assert resp.status_code == 200
        body = resp.json()
        assert body["slug"] == "trend_scanner"
        assert body["tipo"] == "skill"

    def test_slug_inexistente_retorna_404(self):
        resp = client.get("/api/agentes/nao-existe-slug-123")
        assert resp.status_code == 404
        assert "nao encontrado" in resp.json()["detail"].lower()

    def test_response_contract(self):
        """Response deve ter exatamente os campos esperados pelo frontend AgenteDTO."""
        resp = client.get("/api/agentes/copywriter")
        body = resp.json()
        expected = {"slug", "nome", "descricao", "tipo", "conteudo"}
        assert expected == set(body.keys())
