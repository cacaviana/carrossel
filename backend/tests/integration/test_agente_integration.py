"""Integracao Agente (1 caso de uso): GET /api/agentes/{slug}.

Fluxo testado:
- Router -> Factory -> Skills disk -> Response

Apos correcao do Guardiao (JWT obrigatorio), todos os endpoints exigem Bearer.
"""

import pytest


class TestListarAgentes:
    """GET /api/agentes — lista todos os agentes do disco."""

    def test_listar_retorna_array(self, client, admin_headers):
        resp = client.get("/api/agentes", headers=admin_headers)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert isinstance(body, list)

    def test_listar_contract_campos(self, client, admin_headers):
        """Contract: cada item tem slug, nome, descricao, tipo, conteudo."""
        resp = client.get("/api/agentes", headers=admin_headers)
        body = resp.json()
        if not body:
            pytest.skip("Sem agentes no disco")
        for item in body[:3]:
            assert "slug" in item
            assert "nome" in item
            assert "descricao" in item
            assert "tipo" in item
            assert "conteudo" in item


class TestObterPromptAgente:
    """GET /api/agentes/{slug} — obter conteudo (caso de uso 'Obter Prompt')."""

    def test_agente_inexistente_404(self, client, admin_headers):
        resp = client.get("/api/agentes/agente-que-nao-existe", headers=admin_headers)
        assert resp.status_code == 404

    def test_agente_existente_retorna_conteudo(self, client, admin_headers):
        """Se houver qualquer agente listado, buscar por slug deve funcionar."""
        resp_list = client.get("/api/agentes", headers=admin_headers)
        if not resp_list.json():
            pytest.skip("Sem agentes no disco para testar")
        slug = resp_list.json()[0]["slug"]
        resp = client.get(f"/api/agentes/{slug}", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["slug"] == slug
        assert "conteudo" in resp.json()
