"""Testes unitarios — Creator Registry (Config)

Cobre casos de uso:
1. Adicionar Creator
2. Listar Creators
3. Remover Creator (salvar lista sem ele)
4. Salvar Creators Lote

Camadas testadas:
- DTOs (SalvarCreatorRegistryRequest, BuscarCreatorRegistryResponse)
- Mapper (ConfigMapper.dict_to_creator_registry)
- Service (ConfigService.salvar_creator_registry, buscar_creator_registry)
- Router (PUT/GET /api/config/creator-registry)
"""

import sys, os
import json
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from dtos.config.salvar_creator_registry.request import (
    SalvarCreatorRegistryRequest,
    CriadorRequest,
)
from dtos.config.buscar_creator_registry.response import (
    BuscarCreatorRegistryResponse,
    CriadorResponse,
)
from mappers.config_mapper import ConfigMapper
from services.config_service import ConfigService


# ===================================================================
# DTO — SalvarCreatorRegistryRequest / CriadorRequest
# ===================================================================
class TestCriadorRequestDTO:
    def test_cria_criador_completo(self):
        c = CriadorRequest(
            nome="Fulano",
            funcao="TECH_SOURCE",
            plataforma="youtube",
            url="https://yt.com/fulano",
            ativo=True,
        )
        assert c.nome == "Fulano"
        assert c.ativo is True

    def test_url_opcional(self):
        c = CriadorRequest(nome="X", funcao="EXPLAINER", plataforma="twitter")
        assert c.url is None

    def test_ativo_default_true(self):
        c = CriadorRequest(nome="X", funcao="EXPLAINER", plataforma="twitter")
        assert c.ativo is True

    def test_nome_obrigatorio(self):
        with pytest.raises(ValidationError):
            CriadorRequest(funcao="X", plataforma="y")

    def test_funcao_obrigatorio(self):
        with pytest.raises(ValidationError):
            CriadorRequest(nome="N", plataforma="y")

    def test_plataforma_obrigatoria(self):
        with pytest.raises(ValidationError):
            CriadorRequest(nome="N", funcao="F")


class TestSalvarCreatorRegistryRequest:
    def test_lote_vazio_aceito(self):
        req = SalvarCreatorRegistryRequest(criadores=[])
        assert req.criadores == []

    def test_lote_multiplos_criadores(self):
        req = SalvarCreatorRegistryRequest(criadores=[
            {"nome": "A", "funcao": "TECH_SOURCE", "plataforma": "yt"},
            {"nome": "B", "funcao": "EXPLAINER", "plataforma": "tw"},
            {"nome": "C", "funcao": "VIRAL_ENGINE", "plataforma": "ig"},
        ])
        assert len(req.criadores) == 3
        assert req.criadores[0].nome == "A"

    def test_campo_criadores_obrigatorio(self):
        with pytest.raises(ValidationError):
            SalvarCreatorRegistryRequest()


# ===================================================================
# Mapper
# ===================================================================
class TestConfigMapperCreator:
    def test_dict_vazio_retorna_lista_vazia(self):
        resp = ConfigMapper.dict_to_creator_registry({})
        assert resp.criadores == []

    def test_dict_sem_chave_criadores(self):
        resp = ConfigMapper.dict_to_creator_registry({"outra": "coisa"})
        assert resp.criadores == []

    def test_converte_um_criador(self):
        data = {
            "criadores": [
                {
                    "nome": "Carlos Viana",
                    "funcao": "THOUGHT_LEADER",
                    "plataforma": "linkedin",
                    "url": "https://linkedin.com/in/carlos",
                    "ativo": True,
                }
            ]
        }
        resp = ConfigMapper.dict_to_creator_registry(data)
        assert len(resp.criadores) == 1
        c = resp.criadores[0]
        assert c.nome == "Carlos Viana"
        assert c.url == "https://linkedin.com/in/carlos"
        assert c.ativo is True

    def test_defaults_campos_ausentes(self):
        """Campos ausentes no dict devem receber defaults do mapper."""
        data = {"criadores": [{}]}
        resp = ConfigMapper.dict_to_creator_registry(data)
        c = resp.criadores[0]
        assert c.nome == ""
        assert c.funcao == ""
        assert c.plataforma == ""
        assert c.url is None
        assert c.ativo is True

    def test_preserva_ordem(self):
        data = {
            "criadores": [
                {"nome": "Z", "funcao": "f", "plataforma": "p"},
                {"nome": "A", "funcao": "f", "plataforma": "p"},
                {"nome": "M", "funcao": "f", "plataforma": "p"},
            ]
        }
        resp = ConfigMapper.dict_to_creator_registry(data)
        assert [c.nome for c in resp.criadores] == ["Z", "A", "M"]


# ===================================================================
# Service — salvar_creator_registry / buscar_creator_registry
# ===================================================================
class TestConfigServiceCreator:
    @pytest.fixture
    def tmp_configs_dir(self, tmp_path, monkeypatch):
        """Aponta CONFIGS_PATH do service para uma pasta temporaria."""
        monkeypatch.setattr(
            "services.config_service.CONFIGS_PATH", tmp_path
        )
        return tmp_path

    def test_salvar_retorna_sucesso_com_total(self, tmp_configs_dir):
        service = ConfigService()
        req = SalvarCreatorRegistryRequest(criadores=[
            {"nome": "A", "funcao": "TECH_SOURCE", "plataforma": "yt"},
            {"nome": "B", "funcao": "EXPLAINER", "plataforma": "tw"},
        ])
        result = asyncio.run(service.salvar_creator_registry(req))
        assert result["sucesso"] is True
        assert result["total_criadores"] == 2
        assert "2" in result["mensagem"]

    def test_salvar_cria_arquivo_json(self, tmp_configs_dir):
        """INT-04: arquivos sao salvos em tmp/{tenant}/creator_registry.json.

        Chamada sem tenant_id cai em DEFAULT_TENANT_ID ('itvalley').
        """
        from services.config_service import DEFAULT_TENANT_ID
        service = ConfigService()
        req = SalvarCreatorRegistryRequest(criadores=[
            {"nome": "A", "funcao": "TECH_SOURCE", "plataforma": "yt"},
        ])
        asyncio.run(service.salvar_creator_registry(req))
        path = tmp_configs_dir / DEFAULT_TENANT_ID / "creator_registry.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["criadores"][0]["nome"] == "A"

    def test_buscar_arquivo_inexistente_retorna_lista_vazia(self, tmp_configs_dir):
        service = ConfigService()
        result = asyncio.run(service.buscar_creator_registry())
        assert result.criadores == []

    def test_salvar_e_buscar_roundtrip(self, tmp_configs_dir):
        """Adicionar e listar: dados sobrevivem ao roundtrip."""
        service = ConfigService()
        req = SalvarCreatorRegistryRequest(criadores=[
            {"nome": "Carlos", "funcao": "THOUGHT_LEADER", "plataforma": "linkedin",
             "url": "https://lin.k/c", "ativo": True},
            {"nome": "Ana", "funcao": "EXPLAINER", "plataforma": "youtube",
             "url": "https://yt/a", "ativo": False},
        ])
        asyncio.run(service.salvar_creator_registry(req))
        result = asyncio.run(service.buscar_creator_registry())
        assert len(result.criadores) == 2
        assert result.criadores[0].nome == "Carlos"
        assert result.criadores[1].ativo is False

    def test_salvar_sobrescreve_anterior(self, tmp_configs_dir):
        """Remover = salvar a lista sem o creator removido."""
        service = ConfigService()
        # 1. Adiciona 3
        req1 = SalvarCreatorRegistryRequest(criadores=[
            {"nome": "A", "funcao": "F", "plataforma": "p"},
            {"nome": "B", "funcao": "F", "plataforma": "p"},
            {"nome": "C", "funcao": "F", "plataforma": "p"},
        ])
        asyncio.run(service.salvar_creator_registry(req1))
        # 2. Remove B (salva sem B)
        req2 = SalvarCreatorRegistryRequest(criadores=[
            {"nome": "A", "funcao": "F", "plataforma": "p"},
            {"nome": "C", "funcao": "F", "plataforma": "p"},
        ])
        result = asyncio.run(service.salvar_creator_registry(req2))
        assert result["total_criadores"] == 2
        final = asyncio.run(service.buscar_creator_registry())
        nomes = [c.nome for c in final.criadores]
        assert "B" not in nomes
        assert nomes == ["A", "C"]

    def test_salvar_lote_vazio(self, tmp_configs_dir):
        """Salvar lista vazia = remover todos."""
        service = ConfigService()
        req = SalvarCreatorRegistryRequest(criadores=[])
        result = asyncio.run(service.salvar_creator_registry(req))
        assert result["total_criadores"] == 0


# ===================================================================
# INT-04 — multi-tenant: cada tenant tem seu proprio namespace de arquivos
# ===================================================================
class TestConfigServiceMultiTenant:
    """INT-04: Config persiste em pasta por tenant, nunca global."""

    @pytest.fixture
    def tmp_configs_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "services.config_service.CONFIGS_PATH", tmp_path
        )
        return tmp_path

    def test_tenants_diferentes_nao_se_misturam(self, tmp_configs_dir):
        """Dois tenants diferentes: cada um ve seus proprios creators."""
        service = ConfigService()

        req_t1 = SalvarCreatorRegistryRequest(criadores=[
            {"nome": "Tenant1User", "funcao": "F", "plataforma": "p"},
        ])
        req_t2 = SalvarCreatorRegistryRequest(criadores=[
            {"nome": "Tenant2User", "funcao": "F", "plataforma": "p"},
        ])

        asyncio.run(service.salvar_creator_registry(req_t1, tenant_id="tenant1"))
        asyncio.run(service.salvar_creator_registry(req_t2, tenant_id="tenant2"))

        r1 = asyncio.run(service.buscar_creator_registry(tenant_id="tenant1"))
        r2 = asyncio.run(service.buscar_creator_registry(tenant_id="tenant2"))

        assert len(r1.criadores) == 1
        assert r1.criadores[0].nome == "Tenant1User"
        assert len(r2.criadores) == 1
        assert r2.criadores[0].nome == "Tenant2User"

    def test_tenant_desconhecido_retorna_vazio(self, tmp_configs_dir):
        """Tenant sem dados ainda retorna estrutura vazia, nao quebra."""
        service = ConfigService()
        result = asyncio.run(service.buscar_creator_registry(tenant_id="tenant-novo"))
        assert result.criadores == []

    def test_arquivos_salvos_em_pasta_do_tenant(self, tmp_configs_dir):
        """Arquivo fica em tmp/{tenant}/creator_registry.json, nao no root."""
        service = ConfigService()
        req = SalvarCreatorRegistryRequest(criadores=[
            {"nome": "X", "funcao": "F", "plataforma": "p"},
        ])
        asyncio.run(service.salvar_creator_registry(req, tenant_id="acme"))

        expected = tmp_configs_dir / "acme" / "creator_registry.json"
        assert expected.exists(), f"Esperado {expected}"
        # Nao deve existir no root
        global_path = tmp_configs_dir / "creator_registry.json"
        assert not global_path.exists() or global_path.read_text() != expected.read_text(), (
            "Arquivo nao deve ficar no root global"
        )

    def test_migracao_arquivo_global_para_default_tenant(self, tmp_configs_dir):
        """Se um arquivo global legado ja existir, a primeira leitura do default
        tenant copia para a pasta do tenant default (preserva dados antigos)."""
        from services.config_service import DEFAULT_TENANT_ID

        # Cria arquivo global legado
        legacy = tmp_configs_dir / "creator_registry.json"
        legacy.write_text(
            json.dumps({"criadores": [
                {"nome": "Legacy", "funcao": "F", "plataforma": "p", "ativo": True}
            ]}),
            encoding="utf-8",
        )

        service = ConfigService()
        # Sem tenant_id -> cai no DEFAULT_TENANT_ID, deve migrar o arquivo
        result = asyncio.run(service.buscar_creator_registry())
        assert len(result.criadores) == 1
        assert result.criadores[0].nome == "Legacy"

        # Apos a leitura, arquivo deve existir na pasta do tenant default
        migrado = tmp_configs_dir / DEFAULT_TENANT_ID / "creator_registry.json"
        assert migrado.exists()

    def test_migracao_global_nao_afeta_tenant_custom(self, tmp_configs_dir):
        """Arquivo legado global NAO vaza para tenants customizados."""
        # Cria legado
        (tmp_configs_dir / "creator_registry.json").write_text(
            json.dumps({"criadores": [
                {"nome": "Legacy", "funcao": "F", "plataforma": "p"}
            ]}),
            encoding="utf-8",
        )

        service = ConfigService()
        # Tenant custom nao recebe o legado
        result = asyncio.run(service.buscar_creator_registry(tenant_id="outro-tenant"))
        assert result.criadores == []

    def test_brand_palette_tenant_aware(self, tmp_configs_dir):
        """brand_palette tambem e isolado por tenant."""
        from dtos.config.salvar_brand_palette.request import (
            SalvarBrandPaletteRequest,
            CoresRequest,
        )
        service = ConfigService()

        dto1 = SalvarBrandPaletteRequest(
            cores=CoresRequest(
                fundo_principal="#001100",
                destaque_primario="#00FF00",
                destaque_secundario="#00AA00",
                texto_principal="#FFFFFF",
                texto_secundario="#CCCCCC",
            ),
            fonte="Outfit",
            elementos_obrigatorios=[],
            estilo="dark",
        )
        dto2 = SalvarBrandPaletteRequest(
            cores=CoresRequest(
                fundo_principal="#110000",
                destaque_primario="#FF0000",
                destaque_secundario="#AA0000",
                texto_principal="#FFFFFF",
                texto_secundario="#CCCCCC",
            ),
            fonte="Outfit",
            elementos_obrigatorios=[],
            estilo="dark",
        )
        asyncio.run(service.salvar_brand_palette(dto1, tenant_id="t-a"))
        asyncio.run(service.salvar_brand_palette(dto2, tenant_id="t-b"))

        r_a = asyncio.run(service.buscar_brand_palette(tenant_id="t-a"))
        r_b = asyncio.run(service.buscar_brand_palette(tenant_id="t-b"))

        # Cada tenant ve a propria paleta
        assert r_a.cores.destaque_primario == "#00FF00"
        assert r_b.cores.destaque_primario == "#FF0000"


# ===================================================================
# Router — PUT/GET /api/config/creator-registry
# ===================================================================
class TestCreatorRegistryRouter:
    @pytest.fixture
    def client_with_tmp_configs(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "services.config_service.CONFIGS_PATH", tmp_path
        )
        from main import app
        return TestClient(app, raise_server_exceptions=False)

    def test_get_retorna_200(self, client_with_tmp_configs):
        resp = client_with_tmp_configs.get("/api/config/creator-registry")
        assert resp.status_code == 200
        body = resp.json()
        assert "criadores" in body
        assert isinstance(body["criadores"], list)

    def test_put_adicionar_lote(self, client_with_tmp_configs):
        resp = client_with_tmp_configs.put("/api/config/creator-registry", json={
            "criadores": [
                {"nome": "A", "funcao": "TECH_SOURCE", "plataforma": "yt"},
                {"nome": "B", "funcao": "EXPLAINER", "plataforma": "tw"},
            ]
        })
        assert resp.status_code == 200
        assert resp.json()["total_criadores"] == 2

    def test_put_persiste_para_get(self, client_with_tmp_configs):
        client_with_tmp_configs.put("/api/config/creator-registry", json={
            "criadores": [
                {"nome": "Persiste", "funcao": "TECH_SOURCE", "plataforma": "yt"},
            ]
        })
        resp = client_with_tmp_configs.get("/api/config/creator-registry")
        assert resp.status_code == 200
        criadores = resp.json()["criadores"]
        assert len(criadores) == 1
        assert criadores[0]["nome"] == "Persiste"

    def test_put_corpo_invalido_422(self, client_with_tmp_configs):
        """Criador sem campos obrigatorios retorna 422."""
        resp = client_with_tmp_configs.put("/api/config/creator-registry", json={
            "criadores": [{"nome": "Only name"}]
        })
        assert resp.status_code == 422

    def test_put_remover_creator_via_lote_sem_ele(self, client_with_tmp_configs):
        """Caso de uso: Remover Creator = PUT lista nova sem ele."""
        # Seed
        client_with_tmp_configs.put("/api/config/creator-registry", json={
            "criadores": [
                {"nome": "Keep", "funcao": "F", "plataforma": "p"},
                {"nome": "Remove", "funcao": "F", "plataforma": "p"},
            ]
        })
        # PUT sem o "Remove"
        resp = client_with_tmp_configs.put("/api/config/creator-registry", json={
            "criadores": [{"nome": "Keep", "funcao": "F", "plataforma": "p"}]
        })
        assert resp.status_code == 200
        # Verifica
        got = client_with_tmp_configs.get("/api/config/creator-registry").json()
        nomes = [c["nome"] for c in got["criadores"]]
        assert "Remove" not in nomes
        assert nomes == ["Keep"]
