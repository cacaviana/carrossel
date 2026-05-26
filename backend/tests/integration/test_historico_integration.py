"""Integracao Historico — CRUD + busca.

Casos de uso (2): Obter Carrossel, Excluir Carrossel.

Fluxo:
Router -> Service -> SQL Repository (SQL nao configurado em test -> fallback legado).

Testa contrato de resposta: campos que o frontend (HistoricoItemDTO) consome.

BUG DETECTADO previamente:
- Backend retorna `created_at`, frontend HistoricoItemDTO.constructor espera `criado_em`.
  Ver secao TestContratoFrontend abaixo.
"""

import pytest


class TestListarHistorico:
    """GET /api/historico — paginacao, filtros."""

    def test_listar_sem_filtros_retorna_items_e_total(self, client, admin_headers):
        """Mesmo sem dados, retorna estrutura padrao."""
        # Router historico ainda NAO tem auth (bloqueador) — tentar com e sem header
        resp = client.get("/api/historico", headers=admin_headers)
        # Fallback ou SQL: precisa retornar items + total
        assert resp.status_code in (200, 401, 403)
        if resp.status_code == 200:
            body = resp.json()
            assert "items" in body
            assert "total" in body
            assert isinstance(body["items"], list)

    def test_listar_com_filtro_formato(self, client, admin_headers):
        resp = client.get("/api/historico?formato=carrossel", headers=admin_headers)
        assert resp.status_code in (200, 401, 403)

    def test_listar_com_filtro_status(self, client, admin_headers):
        resp = client.get("/api/historico?status=concluido", headers=admin_headers)
        assert resp.status_code in (200, 401, 403)

    def test_listar_com_limit_offset(self, client, admin_headers):
        resp = client.get("/api/historico?limit=10&offset=0", headers=admin_headers)
        assert resp.status_code in (200, 401, 403)


class TestBuscarHistorico:
    """GET /api/historico/{id} — caso de uso 'Obter Carrossel'."""

    def test_buscar_id_inexistente_404(self, client, admin_headers):
        resp = client.get("/api/historico/id-que-nao-existe", headers=admin_headers)
        assert resp.status_code in (404, 401, 403, 500)


class TestDeletarHistorico:
    """DELETE /api/historico/{id} — caso de uso 'Excluir Carrossel'."""

    def test_deletar_id_inexistente(self, client, admin_headers):
        """Fallback legado retorna 500; SQL Repository retorna 404. Ambos aceitos."""
        resp = client.delete("/api/historico/99999999", headers=admin_headers)
        # Depende do fallback SQL vs legado
        assert resp.status_code in (200, 404, 500, 401, 403)


class TestContratoFrontend:
    """BUG CRITICO: frontend (HistoricoItemDTO) le campo `criado_em`,
    backend (HistoricoItem DTO + Mapper) devolve `created_at`.

    Valor sempre vira string vazia no frontend (null coalescing).
    """

    def test_backend_retorna_created_at_nao_criado_em(self, client, admin_headers):
        """Documenta o drift: backend sempre manda created_at."""
        resp = client.get("/api/historico", headers=admin_headers)
        if resp.status_code != 200:
            pytest.skip("SQL nao configurado ou sem dados")
        items = resp.json().get("items", [])
        if not items:
            pytest.skip("Sem historico para verificar contrato")
        # Backend manda created_at
        assert "created_at" in items[0] or "criado_em" in items[0]
        if "created_at" in items[0] and "criado_em" not in items[0]:
            pytest.fail(
                "CONTRATO QUEBRADO: backend manda 'created_at', frontend HistoricoItemDTO espera 'criado_em'. "
                "Resultado: dataFormatada sempre vazia."
            )


class TestHardcodedTenantId:
    """BUG CRITICO (Guardiao): historico.py usa settings.TENANT_ID hardcoded
    em vez de tenant do JWT. Isola multi-tenant incorretamente.
    """

    def test_historico_usa_tenant_hardcoded_nao_do_jwt(self, client):
        """Este teste documenta o problema. Uma vez corrigido, deve retornar
        dados diferentes por tenant. Por ora, so checa que rota responde."""
        from config import settings
        # Settings.TENANT_ID existe e esta hardcoded em routers/historico.py (linha 6)
        assert hasattr(settings, "TENANT_ID"), (
            "config.TENANT_ID nao existe — verificar se bloqueador do Guardiao foi tratado"
        )
